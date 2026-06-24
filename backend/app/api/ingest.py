import json
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core import security
from app.db.postgres import get_db
from app.db.redis import get_redis_client
from app.db.clickhouse import get_clickhouse_client
from app.models.postgres_models import Agent
from app.schemas.ingest import IngestPayload, IngestResponse

router = APIRouter()

def parse_float(val: Any) -> float:
    try:
        if isinstance(val, str) and val == "-":
            return 0.0
        return float(val)
    except:
        return 0.0

def parse_int(val: Any) -> int:
    try:
        if isinstance(val, str) and val == "-":
            return 0
        return int(val)
    except:
        return 0

@router.post("/nginx", response_model=IngestResponse)
async def ingest_nginx(
    payload: IngestPayload,
    x_agent_id: str = Header(None),
    x_agent_token: str = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if not x_agent_id or not x_agent_token:
        raise HTTPException(status_code=401, detail="Missing agent credentials")

    # Validate agent
    stmt = select(Agent).where(Agent.id == x_agent_id)
    result = await db.execute(stmt)
    agent = result.scalars().first()
    
    if not agent or not security.verify_password(x_agent_token, agent.token_hash):
        raise HTTPException(status_code=401, detail="Invalid agent credentials")
    
    if payload.agent_id != str(agent.id) and payload.agent_id != agent.name:
        raise HTTPException(status_code=400, detail="Agent ID mismatch in payload")

    # Update agent last seen
    agent.last_seen_at = datetime.utcnow()
    await db.commit()

    ch_client = get_clickhouse_client()
    redis_client = await get_redis_client()

    inserted_count = 0
    failed_count = 0
    validation_errors = []

    ch_rows = []
    
    now = datetime.now(timezone.utc)

    for entry in payload.logs:
        try:
            # Parse time
            try:
                ts = datetime.fromisoformat(entry.time.replace("Z", "+00:00"))
            except ValueError:
                ts = now

            status_code = parse_int(entry.status)
            body_bytes = parse_int(entry.body_bytes)
            request_time = parse_float(entry.request_time)
            
            # Extract method, uri from request if missing
            method = entry.method
            uri = entry.uri
            protocol = ""
            if entry.request and (not method or not uri):
                parts = entry.request.split()
                if len(parts) >= 1: method = parts[0]
                if len(parts) >= 2: uri = parts[1]
                if len(parts) >= 3: protocol = parts[2]
            
            # Upstream time could be a string of multiple values like "0.010, 0.020"
            upstream_time_str = str(entry.upstream_response_time)
            if "," in upstream_time_str:
                upstream_time_str = upstream_time_str.split(",")[-1].strip()
            upstream_response_time = parse_float(upstream_time_str)

            status_class = f"{status_code // 100}xx" if 100 <= status_code < 600 else "other"
            is_error = 1 if status_code >= 400 else 0
            is_slow = 1 if request_time >= settings.SLOW_REQUEST_THRESHOLD_SECONDS else 0

            row = [
                ts.replace(tzinfo=None), # ClickHouse client converts natively
                str(agent.id),
                agent.server_name,
                entry.real_ip or "",
                entry.remote or "",
                entry.cf_ip or "",
                entry.xff or "",
                entry.user or "",
                entry.scheme or "",
                entry.host or "",
                method or "",
                uri or "",
                entry.args or "",
                entry.request or "",
                protocol,
                status_code,
                status_class,
                body_bytes,
                entry.http_ref or "",
                entry.agent or "",
                request_time,
                upstream_response_time,
                entry.upstream_addr or "",
                is_error,
                is_slow
            ]
            ch_rows.append(row)
            inserted_count += 1

            # Publish realtime event to Redis
            event = {
                "type": "nginx_request",
                "ts": ts.isoformat(),
                "agent_id": str(agent.id),
                "server_name": agent.server_name,
                "host": entry.host or "",
                "source": agent.server_name,
                "destination": entry.upstream_addr or "client",
                "method": method or "",
                "uri": uri or "",
                "status": status_code,
                "status_class": status_class,
                "request_time": request_time,
                "upstream_response_time": upstream_response_time,
                "real_ip": entry.real_ip or ""
            }
            # We don't await here to not block the batch. Wait, Redis is async so we should queue it
            await redis_client.publish("nginx_realtime_events", json.dumps(event))

        except Exception as e:
            failed_count += 1
            validation_errors.append(str(e))

    # Insert batch to ClickHouse
    if ch_rows:
        try:
            columns = [
                'ts', 'agent_id', 'server_name', 'real_ip', 'remote', 'cf_ip', 'xff', 
                'nginx_user', 'scheme', 'host', 'method', 'uri', 'args', 'request', 'protocol', 
                'status', 'status_class', 'body_bytes', 'http_ref', 'user_agent', 
                'request_time', 'upstream_response_time', 'upstream_addr', 'is_error', 'is_slow'
            ]
            ch_client.insert(
                f'{settings.CLICKHOUSE_DB}.nginx_access_logs', 
                ch_rows, 
                column_names=columns
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ClickHouse insert failed: {str(e)}")

    return IngestResponse(
        inserted_count=inserted_count,
        failed_count=failed_count,
        validation_errors=validation_errors[:10] # limit error messages
    )
