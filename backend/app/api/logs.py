from typing import Any, Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime, timedelta

from app.db.clickhouse import get_clickhouse_client
from app.core.config import settings
from app.api import deps
from app.models.postgres_models import User

router = APIRouter()

@router.get("")
async def get_logs(
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    agent_id: Optional[str] = None,
    host: Optional[str] = None,
    status_class: Optional[str] = None,
    is_error: Optional[bool] = None,
    is_slow: Optional[bool] = None,
    mode: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    client = get_clickhouse_client()
    
    if mode == "topology":
        to_time = datetime.utcnow()
        from_time = to_time - timedelta(seconds=settings.TOPOLOGY_LOG_WINDOW_SECONDS)
    else:
        # Default time range: last 24 hours
        if not to_time:
            to_time = datetime.utcnow()
        if not from_time:
            from_time = to_time - timedelta(hours=24)
        
    query = f"""
        SELECT 
            ts, agent_id, server_name, scheme, protocol, real_ip, host, method, uri, 
            status, status_class, request_time, upstream_response_time, 
            upstream_addr, user_agent
        FROM {settings.CLICKHOUSE_DB}.nginx_access_logs
        WHERE ts >= %(from_time)s AND ts <= %(to_time)s
    """
    
    params = {
        "from_time": from_time.strftime("%Y-%m-%d %H:%M:%S"),
        "to_time": to_time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if agent_id:
        query += " AND agent_id = %(agent_id)s"
        params["agent_id"] = agent_id
    if host:
        query += " AND host = %(host)s"
        params["host"] = host
    if status_class:
        query += " AND status_class = %(status_class)s"
        params["status_class"] = status_class
    if is_error is not None:
        query += " AND is_error = %(is_error)s"
        params["is_error"] = 1 if is_error else 0
    if is_slow is not None:
        query += " AND is_slow = %(is_slow)s"
        params["is_slow"] = 1 if is_slow else 0
        
    query += " ORDER BY ts DESC LIMIT %(limit)s OFFSET %(offset)s"
    params["limit"] = limit
    params["offset"] = offset
    
    try:
        result = client.query(query, parameters=params)
        
        # Format the result to dictionary
        columns = result.column_names
        rows = result.result_rows
        
        formatted_rows = [dict(zip(columns, row)) for row in rows]
        
        return {
            "data": formatted_rows,
            "count": len(formatted_rows),
            "limit": limit,
            "offset": offset,
            "server_time": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ClickHouse query failed: {str(e)}")

@router.get("/errors")
async def get_errors(
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    client = get_clickhouse_client()
    if not to_time: to_time = datetime.utcnow()
    if not from_time: from_time = to_time - timedelta(hours=24)

    query = f"""
        SELECT ts, agent_id, server_name, real_ip, host, method, uri, status, request_time
        FROM {settings.CLICKHOUSE_DB}.nginx_access_logs
        WHERE ts >= %(from_time)s AND ts <= %(to_time)s AND is_error = 1
        ORDER BY ts DESC LIMIT %(limit)s OFFSET %(offset)s
    """
    count_query = f"""
        SELECT count()
        FROM {settings.CLICKHOUSE_DB}.nginx_access_logs
        WHERE ts >= %(from_time)s AND ts <= %(to_time)s AND is_error = 1
    """
    params = {
        "from_time": from_time.strftime("%Y-%m-%d %H:%M:%S"),
        "to_time": to_time.strftime("%Y-%m-%d %H:%M:%S"),
        "limit": limit,
        "offset": offset
    }
    try:
        res = client.query(query, parameters=params)
        count_res = client.query(count_query, parameters=params)
        total = count_res.result_rows[0][0] if count_res.result_rows else 0
        return {
            "data": [dict(zip(res.column_names, r)) for r in res.result_rows],
            "total": total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/slow-requests")
async def get_slow_requests(
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    client = get_clickhouse_client()
    if not to_time: to_time = datetime.utcnow()
    if not from_time: from_time = to_time - timedelta(hours=24)

    query = f"""
        SELECT ts, agent_id, server_name, real_ip, host, method, uri, status, request_time, upstream_response_time
        FROM {settings.CLICKHOUSE_DB}.nginx_access_logs
        WHERE ts >= %(from_time)s AND ts <= %(to_time)s AND is_slow = 1
        ORDER BY ts DESC LIMIT %(limit)s OFFSET %(offset)s
    """
    count_query = f"""
        SELECT count()
        FROM {settings.CLICKHOUSE_DB}.nginx_access_logs
        WHERE ts >= %(from_time)s AND ts <= %(to_time)s AND is_slow = 1
    """
    params = {
        "from_time": from_time.strftime("%Y-%m-%d %H:%M:%S"),
        "to_time": to_time.strftime("%Y-%m-%d %H:%M:%S"),
        "limit": limit,
        "offset": offset
    }
    try:
        res = client.query(query, parameters=params)
        count_res = client.query(count_query, parameters=params)
        total = count_res.result_rows[0][0] if count_res.result_rows else 0
        return {
            "data": [dict(zip(res.column_names, r)) for r in res.result_rows],
            "total": total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

