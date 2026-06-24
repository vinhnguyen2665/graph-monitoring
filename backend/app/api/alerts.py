from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.db.postgres import get_db
from app.models.postgres_models import AlertRule, AlertEvent, User
from app.api import deps

router = APIRouter()

class AlertRuleCreate(BaseModel):
    name: str
    condition_type: str
    threshold: float
    duration_minutes: int = 5
    notification_channel: str = "console"

class AlertRuleResponse(BaseModel):
    id: UUID
    name: str
    enabled: bool
    condition_type: str
    threshold: float
    duration_minutes: int
    notification_channel: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AlertEventResponse(BaseModel):
    id: UUID
    rule_id: UUID
    rule_name: str
    event_type: str
    value: float
    threshold: float
    message: str | None
    resolved: bool
    created_at: datetime
    resolved_at: datetime | None

    class Config:
        from_attributes = True

@router.get("/rules", response_model=List[AlertRuleResponse])
async def get_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    stmt = select(AlertRule)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/rules", response_model=AlertRuleResponse)
async def create_rule(
    rule_in: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    rule = AlertRule(
        name=rule_in.name,
        condition_type=rule_in.condition_type,
        threshold=rule_in.threshold,
        duration_minutes=rule_in.duration_minutes,
        notification_channel=rule_in.notification_channel,
        enabled=True
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule

@router.get("/events", response_model=List[AlertEventResponse])
async def get_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    stmt = select(AlertEvent).order_by(AlertEvent.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/events/{event_id}/resolve", response_model=AlertEventResponse)
async def resolve_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    stmt = select(AlertEvent).where(AlertEvent.id == event_id)
    res = await db.execute(stmt)
    event = res.scalars().first()
    if not event:
        raise HTTPException(status_code=404, detail="Alert event not found")
    
    event.resolved = True
    event.resolved_at = datetime.utcnow()
    await db.commit()
    return event
