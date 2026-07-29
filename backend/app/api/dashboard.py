from typing import Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime, timedelta

from app.db.clickhouse import get_clickhouse_client
from app.core.config import settings
from app.api import deps
from app.models.postgres_models import User

router = APIRouter()

import math

@router.get("/overview")
async def get_overview(
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    client = get_clickhouse_client()
    
    if not to_time: to_time = datetime.utcnow()
    if not from_time: from_time = to_time - timedelta(hours=24)
        
    query = f"""
        SELECT 
            count() as total_requests,
            ifNull(sum(is_error), 0) as total_errors,
            ifNull(sum(is_slow), 0) as total_slow,
            nanToZero(avg(request_time)) as avg_latency,
            nanToZero(quantile(0.95)(request_time)) as p95_latency,
            ifNull(sum(body_bytes), 0) as total_bytes
        FROM {settings.CLICKHOUSE_DB}.nginx_access_logs
        WHERE ts >= %(from_time)s AND ts <= %(to_time)s
    """
    
    params = {
        "from_time": from_time.strftime("%Y-%m-%d %H:%M:%S"),
        "to_time": to_time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        result = client.query(query, parameters=params)
        columns = result.column_names
        rows = result.result_rows
        
        if not rows:
            return {
                "total_requests": 0, "total_errors": 0, "total_slow": 0,
                "avg_latency": 0.0, "p95_latency": 0.0, "total_bytes": 0
            }
            
        raw_dict = dict(zip(columns, rows[0]))
        cleaned_dict = {}
        for k, v in raw_dict.items():
            if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
                cleaned_dict[k] = 0
            else:
                cleaned_dict[k] = v
        return cleaned_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/request-timeseries")
async def get_request_timeseries(
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    client = get_clickhouse_client()
    if not to_time: to_time = datetime.utcnow()
    if not from_time: from_time = to_time - timedelta(hours=24)
        
    query = f"""
        SELECT 
            toStartOfMinute(ts) as time_bucket,
            count() as count
        FROM {settings.CLICKHOUSE_DB}.nginx_access_logs
        WHERE ts >= %(from_time)s AND ts <= %(to_time)s
        GROUP BY time_bucket
        ORDER BY time_bucket ASC
    """
    params = {
        "from_time": from_time.strftime("%Y-%m-%d %H:%M:%S"),
        "to_time": to_time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    result = client.query(query, parameters=params)
    return [dict(zip(result.column_names, row)) for row in result.result_rows]

@router.get("/status-timeseries")
async def get_status_timeseries(
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    client = get_clickhouse_client()
    if not to_time: to_time = datetime.utcnow()
    if not from_time: from_time = to_time - timedelta(hours=24)
        
    query = f"""
        SELECT 
            status_class,
            count() as count
        FROM {settings.CLICKHOUSE_DB}.nginx_access_logs
        WHERE ts >= %(from_time)s AND ts <= %(to_time)s
        GROUP BY status_class
        ORDER BY count DESC
    """
    params = {
        "from_time": from_time.strftime("%Y-%m-%d %H:%M:%S"),
        "to_time": to_time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    result = client.query(query, parameters=params)
    return [dict(zip(result.column_names, row)) for row in result.result_rows]
