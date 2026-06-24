import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.postgres import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="viewer", nullable=False) # admin, operator, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    server_name = Column(String, nullable=False, index=True)
    hostname = Column(String)
    ip_address = Column(String)
    log_path = Column(String)
    token_hash = Column(String, nullable=False)
    status = Column(String, default="offline")
    last_seen_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    condition_type = Column(String, nullable=False)
    threshold = Column(Float, nullable=False)
    duration_minutes = Column(Integer, default=5)
    filters = Column(JSONB, default=dict)
    notification_channel = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TopologyNodeConfig(Base):
    __tablename__ = "topology_node_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_key = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String)
    node_type = Column(String) # nginx, upstream, client
    position_x = Column(Float)
    position_y = Column(Float)
    color = Column(String)
    icon = Column(String)
    metadata_json = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AlertEvent(Base):
    __tablename__ = "alert_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), nullable=False)
    rule_name = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    message = Column(String)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

