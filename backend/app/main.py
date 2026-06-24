import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.db.postgres import Base, engine, AsyncSessionLocal
from app.db.clickhouse import init_clickhouse_schema
from app.core import security
from app.models import postgres_models
from app.models.postgres_models import User, AlertRule
from sqlalchemy import select

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize Postgres Schema (with retry loop in case DB is still starting up in Docker)
    retries = 5
    db_connected = False
    while retries > 0:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            db_connected = True
            print("PostgreSQL tables checked/created successfully.")
            break
        except Exception as e:
            print(f"PostgreSQL not ready yet ({retries} retries left): {e}")
            retries -= 1
            await asyncio.sleep(2)
            
    if not db_connected:
        print("Could not connect to PostgreSQL. Startup continuing anyway...")
        
    # 2. Initialize ClickHouse Schema
    try:
        init_clickhouse_schema()
    except Exception as e:
        print(f"ClickHouse init failed: {e}")
        
    # 3. Seed Default Admin User & Alert Rules
    if db_connected:
        try:
            async with AsyncSessionLocal() as db:
                # User seeding
                stmt = select(User).limit(1)
                res = await db.execute(stmt)
                user = res.scalars().first()
                if not user:
                    print("Seeding default admin user...")
                    admin_user = User(
                        email="admin@admin.com",
                        username="admin",
                        hashed_password=security.get_password_hash("adminpassword"),
                        full_name="System Administrator",
                        role="admin",
                        is_active=True
                    )
                    db.add(admin_user)
                    await db.commit()
                    print("Default admin user created successfully.")

                # Alert Rules seeding
                rules_stmt = select(AlertRule).limit(1)
                rules_res = await db.execute(rules_stmt)
                existing_rule = rules_res.scalars().first()
                if not existing_rule:
                    print("Seeding default security alert rules...")
                    ddos_rule = AlertRule(
                        name="DDoS Threat Detection",
                        condition_type="ddos_attempt",
                        threshold=1000.0,
                        duration_minutes=1,
                        enabled=True,
                        notification_channel="console"
                    )
                    scan_rule = AlertRule(
                        name="Directory/Vulnerability Scanning",
                        condition_type="scan_attempt",
                        threshold=100.0,
                        duration_minutes=2,
                        enabled=True,
                        notification_channel="console"
                    )
                    db.add(ddos_rule)
                    db.add(scan_rule)
                    await db.commit()
                    print("Default alert rules seeded successfully.")
        except Exception as e:
            print(f"Seeding default data failed: {e}")
            
    yield

app = FastAPI(
    title="Nginx Monitoring System",
    description="Backend API for the Nginx Monitoring Dashboard",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api import auth, agents, ingest, logs, dashboard, ws, alerts, users
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["ingest"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(ws.router, prefix="/api/ws", tags=["ws"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
