from typing import Optional, Union
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class AgentBase(BaseModel):
    name: str
    server_name: str
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    log_path: Optional[str] = None
    fingerprint: Optional[str] = None

class AgentCreate(AgentBase):
    pass

class AgentRegisterRequest(BaseModel):
    server_name: str
    name: Optional[str] = None
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    log_path: Optional[str] = None
    fingerprint: str

class AgentRegisterResponse(BaseModel):
    agent_id: Union[UUID, str]
    agent_token: str
    server_name: str
    status: str

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    server_name: Optional[str] = None
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    log_path: Optional[str] = None
    status: Optional[str] = None

class AgentInDB(AgentBase):
    model_config = ConfigDict(from_attributes=True)

    id: Union[UUID, str]
    status: str
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class AgentResponse(AgentInDB):
    pass

class AgentCreateResponse(AgentInDB):
    token: str # Only returned once when created or rotated
