import secrets
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.core import security
from app.db.postgres import get_db
from app.models.postgres_models import Agent, User
from app.schemas.agent import (
    AgentCreate, AgentUpdate, AgentResponse, AgentCreateResponse,
    AgentRegisterRequest, AgentRegisterResponse
)
from app.api import deps

router = APIRouter()

def generate_agent_token() -> str:
    return secrets.token_urlsafe(32)

@router.post("/register", response_model=AgentRegisterResponse)
async def auto_register_agent(
    *,
    db: AsyncSession = Depends(get_db),
    agent_in: AgentRegisterRequest,
) -> Any:
    """
    Auto-register an agent connecting for the first time or re-registering via fingerprint.
    Does not require admin JWT token so agents can onboard dynamically.
    """
    # 1. First check by fingerprint
    stmt = select(Agent).where(Agent.fingerprint == agent_in.fingerprint)
    result = await db.execute(stmt)
    agent = result.scalars().first()

    # 2. Fallback check by server_name if fingerprint didn't match
    if not agent:
        stmt = select(Agent).where(Agent.server_name == agent_in.server_name)
        result = await db.execute(stmt)
        agent = result.scalars().first()

    token = generate_agent_token()
    token_hash = security.get_password_hash(token)

    if agent:
        # Re-register existing agent: update details and issue new token
        agent.server_name = agent_in.server_name
        if agent_in.name:
            agent.name = agent_in.name
        if agent_in.hostname:
            agent.hostname = agent_in.hostname
        if agent_in.ip_address:
            agent.ip_address = agent_in.ip_address
        if agent_in.log_path:
            agent.log_path = agent_in.log_path
        agent.fingerprint = agent_in.fingerprint
        agent.token_hash = token_hash
        agent.status = "online"
        await db.commit()
        await db.refresh(agent)
        status_msg = "re-registered"
    else:
        # Create brand new agent
        agent = Agent(
            name=agent_in.name or agent_in.server_name,
            server_name=agent_in.server_name,
            hostname=agent_in.hostname,
            ip_address=agent_in.ip_address,
            log_path=agent_in.log_path,
            fingerprint=agent_in.fingerprint,
            token_hash=token_hash,
            status="online"
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        status_msg = "registered"

    return AgentRegisterResponse(
        agent_id=agent.id,
        agent_token=token,
        server_name=agent.server_name,
        status=status_msg
    )

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
