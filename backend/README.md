# Nginx Monitor - Backend API Server

High-performance API server built with FastAPI to manage authentication, agent coordination, and process real-time log ingestion stream.

## 🛠️ Technology Stack
* **Web Framework**: FastAPI (Asynchronous Python)
* **Databases**:
  * **PostgreSQL**: Metadata storage (User accounts, Agent tokens, Alerts) via SQLAlchemy & Alembic.
  * **ClickHouse**: High-volume Nginx access logs ingestion & querying via `clickhouse-connect`.
  * **Redis**: Real-time Pub/Sub broker for push notifications via WebSocket.
* **Authentication**: JWT token-based authentication with bcrypt password hashing.

---

## 🚀 Local Development Setup

### 1. Requirements
* Python 3.10 or higher
* Databases running (via root `docker compose up -d`)

### 2. Set Up Virtual Environment & Dependencies
Create a virtual environment and install backend dependencies:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Setup Configuration
Copy the `.env.example` file and customize it if needed:
```bash
cp .env.example .env
```
Default parameters in `.env`:
* `POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=postgrespassword`, `POSTGRES_DB=net_monitoring`
* `CLICKHOUSE_USER=default`, `CLICKHOUSE_PASSWORD=clickhousepassword`, `CLICKHOUSE_DB=net_monitoring`
* `REDIS_HOST=localhost`, `REDIS_PORT=6379`
* `JWT_SECRET_KEY` (Auto-generated fallback or custom)

### 4. Database Migrations (PostgreSQL)
Run Alembic migrations to initialize PostgreSQL schema:
```bash
source venv/bin/activate
alembic upgrade head
```

### 5. Running the Backend Server
Start the Uvicorn development server:
```bash
source venv/bin/activate
python app/main.py
```
Or run directly with Uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Once started:
* **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`
* **Redoc UI**: `http://localhost:8000/redoc`

---

## 🔑 Default Administrator Credentials
On server startup, if no users exist in PostgreSQL, the backend automatically seeds a default admin account:
* **Email**: `admin@admin.com`
* **Password**: `adminpassword`

Use these credentials to log in to the frontend dashboard.

---

## 📡 API Endpoints

### Auth Module (`/api/auth`)
* `POST /api/auth/login`: Auths user and returns JWT token.
* `GET /api/auth/me`: Gets currently logged-in user profile.

### Log Ingestion & Querying (`/api/ingest`, `/api/logs`)
* `POST /api/ingest/nginx`: Main ingestion endpoint for Python agents (requires `X-Agent-Id` and `X-Agent-Token` headers).
* `GET /api/logs`: Query paginated Nginx logs from ClickHouse.
* `GET /api/logs/errors`: Query 4xx/5xx logs from ClickHouse.
* `GET /api/logs/slow-requests`: Query requests taking longer than slow threshold.

### Dashboard Analytics (`/api/dashboard`)
* `GET /api/dashboard/overview`: Get aggregated stats (Total requests, error rates, slow counts).
* `GET /api/dashboard/request-timeseries`: Get request counts over time for charts.
* `GET /api/dashboard/status-timeseries`: Get breakdown of status code distributions.

### WebSockets (`/api/ws`)
* `WS /api/ws/realtime`: Establishes raw persistent connection for listening to incoming Nginx access events via Redis Pub/Sub.
