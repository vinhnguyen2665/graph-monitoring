from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class NginxLogEntry(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    time: str
    real_ip: Optional[str] = None
    remote: Optional[str] = None
    cf_ip: Optional[str] = None
    xff: Optional[str] = None
    user: Optional[str] = None
    scheme: Optional[str] = None
    host: Optional[str] = None
    method: Optional[str] = None
    uri: Optional[str] = None
    args: Optional[str] = None
    request: Optional[str] = None
    status: Union[int, str] = 0
    body_bytes: Union[int, str] = 0
    http_ref: Optional[str] = None
    agent: Optional[str] = None
    request_time: Union[float, str] = 0.0
    upstream_response_time: Union[float, str, None] = 0.0
    upstream_addr: Optional[str] = None

class IngestPayload(BaseModel):
    agent_id: str
    server_time: str
    logs: List[NginxLogEntry]

class IngestResponse(BaseModel):
    inserted_count: int
    failed_count: int
    validation_errors: List[str]
