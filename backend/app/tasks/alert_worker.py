import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.db.postgres import AsyncSessionLocal
from app.db.clickhouse import get_clickhouse_client
from app.models.postgres_models import AlertRule, AlertEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alert_worker")

async def evaluate_rules():
    async with AsyncSessionLocal() as db:
        stmt = select(AlertRule).where(AlertRule.enabled == True)
        result = await db.execute(stmt)
        rules = result.scalars().all()
        
        ch_client = get_clickhouse_client()
        
        for rule in rules:
            try:
                # Calculate the time window
                to_time = datetime.utcnow()
                from_time = to_time - timedelta(minutes=rule.duration_minutes)
                
                from_str = from_time.strftime("%Y-%m-%d %H:%M:%S")
                to_str = to_time.strftime("%Y-%m-%d %H:%M:%S")
                
                # Default query parameters
                ch_params = {"from_time": from_str, "to_time": to_str}
                
                # Check metrics in ClickHouse
                value = 0.0
                trigger_alert = False
                alert_msg = None
                
                if rule.condition_type == "error_rate":
                    query = f"""
                        SELECT 
                            count() as total,
                            sum(is_error) as errors
                        FROM {settings.CLICKHOUSE_DB}.nginx_access_logs
                        WHERE ts >= %(from_time)s AND ts <= %(to_time)s
                    """
                    res = ch_client.query(query, parameters=ch_params)
                    if res.result_rows:
                        total, errors = res.result_rows[0]
                        if total > 0:
                            value = (errors / total) * 100.0
                            if value >= rule.threshold:
                                trigger_alert = True
                                
                elif rule.condition_type == "status_5xx_count":
                    query = f"""
                        SELECT count() 
                        FROM {settings.CLICKHOUSE_DB}.nginx_access_logs
                        WHERE ts >= %(from_time)s AND ts <= %(to_time)s AND status >= 500 AND status < 600
                    """
                    res = ch_client.query(query, parameters=ch_params)
                    if res.result_rows:
                        value = float(res.result_rows[0][0])
                        if value >= rule.threshold:
                            trigger_alert = True
                            
                elif rule.condition_type == "slow_request_count":
                    query = f"""
                        SELECT count() 
                        FROM {settings.CLICKHOUSE_DB}.nginx_access_logs
                        WHERE ts >= %(from_time)s AND ts <= %(to_time)s AND is_slow = 1
                    """
                    res = ch_client.query(query, parameters=ch_params)
                    if res.result_rows:
                        value = float(res.result_rows[0][0])
                        if value >= rule.threshold:
                            trigger_alert = True

                elif rule.condition_type == "ddos_attempt":
                    query = f"""
                        SELECT real_ip, count() as req_count
                        FROM {settings.CLICKHOUSE_DB}.nginx_access_logs
                        WHERE ts >= %(from_time)s AND ts <= %(to_time)s
                        GROUP BY real_ip
                        ORDER BY req_count DESC
                        LIMIT 1
                    """
                    res = ch_client.query(query, parameters=ch_params)
                    if res.result_rows:
                        ip, req_count = res.result_rows[0]
                        value = float(req_count)
                        if value >= rule.threshold:
                            trigger_alert = True
                            alert_msg = f"DDoS threat detected: IP {ip} sent {int(value)} requests in {rule.duration_minutes} minutes (Threshold: {rule.threshold})."

                elif rule.condition_type == "scan_attempt":
                    query = f"""
                        SELECT real_ip, count() as scan_count
                        FROM {settings.CLICKHOUSE_DB}.nginx_access_logs
                        WHERE ts >= %(from_time)s AND ts <= %(to_time)s AND (status = 404 OR status = 403 OR status = 400)
                        GROUP BY real_ip
                        ORDER BY scan_count DESC
                        LIMIT 1
                    """
                    res = ch_client.query(query, parameters=ch_params)
                    if res.result_rows:
                        ip, scan_count = res.result_rows[0]
                        value = float(scan_count)
                        if value >= rule.threshold:
                            trigger_alert = True
                            alert_msg = f"Vulnerability scanning detected: IP {ip} generated {int(value)} 400/403/404 errors in {rule.duration_minutes} minutes (Threshold: {rule.threshold})."
                
                # Alert handling logic
                event_stmt = select(AlertEvent).where(
                    AlertEvent.rule_id == rule.id,
                    AlertEvent.resolved == False
                )
                event_result = await db.execute(event_stmt)
                active_event = event_result.scalars().first()
                
                if trigger_alert:
                    if not active_event:
                        logger.warning(f"ALERT TRIGGERED: {rule.name} (Value: {value}, Threshold: {rule.threshold})")
                        alert_event = AlertEvent(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            event_type=rule.condition_type,
                            value=value,
                            threshold=rule.threshold,
                            message=alert_msg or f"Condition {rule.condition_type} reached value {value:.2f} (Threshold: {rule.threshold})"
                        )
                        db.add(alert_event)
                else:
                    if active_event:
                        logger.info(f"ALERT RESOLVED: {rule.name}")
                        active_event.resolved = True
                        active_event.resolved_at = datetime.utcnow()
                        
                await db.commit()
                
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")

async def start_worker():
    logger.info("Starting alert worker...")
    while True:
        try:
            await evaluate_rules()
        except Exception as e:
            logger.error(f"Error in alert worker loop: {e}")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(start_worker())
