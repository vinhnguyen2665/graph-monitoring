import secrets
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.core import security
from app.db.postgres import get_db
from app.models.postgres_models import Agent, User
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse, AgentCreateResponse
from app.api import deps

router = APIRouter()

def generate_agent_token() -> str:
    return secrets.token_urlsafe(32)

@router.post("", response_model=AgentCreateResponse)
async def create_agent(
    *,
    db: AsyncSession = Depends(get_db),
    agent_in: AgentCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    # Check if server_name is already used
    stmt = select(Agent).where(Agent.server_name == agent_in.server_name)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Server name already registered")
        
    token = generate_agent_token()
    token_hash = security.get_password_hash(token)
    
    agent = Agent(
        **agent_in.model_dump(),
        token_hash=token_hash
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    
    # We return the raw token only once
    response_data = AgentCreateResponse.model_validate(agent).model_dump()
    response_data["token"] = token
    return response_data

@router.get("", response_model=List[AgentResponse])
async def read_agents(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    stmt = select(Agent).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{agent_id}", response_model=AgentResponse)
async def read_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    stmt = select(Agent).where(Agent.id == agent_id)
    result = await db.execute(stmt)
    agent = result.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    agent_in: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    stmt = select(Agent).where(Agent.id == agent_id)
    result = await db.execute(stmt)
    agent = result.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    update_data = agent_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
        
    await db.commit()
    await db.refresh(agent)
    return agent

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    stmt = select(Agent).where(Agent.id == agent_id)
    result = await db.execute(stmt)
    agent = result.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    await db.delete(agent)
    await db.commit()
    return {"status": "success"}

@router.post("/{agent_id}/rotate-token")
async def rotate_agent_token(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    stmt = select(Agent).where(Agent.id == agent_id)
    result = await db.execute(stmt)
    agent = result.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    token = generate_agent_token()
    token_hash = security.get_password_hash(token)
    
    agent.token_hash = token_hash
    await db.commit()
    
    return {"token": token}
