import os
import sys
import time
import json
import random
import datetime
import requests
import secrets
from pathlib import Path

# Add backend directory to sys.path to import our app configurations and models
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
sys.path.append(BACKEND_DIR)

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core import security
from app.models.postgres_models import Agent

# Setup SQLAlchemy sync engine to register/seed dummy agent
engine = create_engine(settings.SQLALCHEMY_SYNC_DATABASE_URI)
Session = sessionmaker(bind=engine)

DEMO_AGENT_NAME = "demo-agent"
DEMO_SERVER_NAME = "meteo.zero9vn.com"
DEMO_TOKEN = "demo-secret-agent-token-123456"

# Ensure log directory exists
AGENT_DIR = Path(__file__).parent
LOG_PATH = AGENT_DIR / "dummy_access.log"
CONFIG_PATH = AGENT_DIR / "config.yml"

def register_agent():
    print("Checking/registering demo agent in PostgreSQL...")
    session = Session()
    try:
        # Check if agent already exists
        stmt = select(Agent).where(Agent.name == DEMO_AGENT_NAME)
        agent = session.execute(stmt).scalars().first()
        
        if not agent:
            print("Demo agent not found. Creating a new one...")
            token_hash = security.get_password_hash(DEMO_TOKEN)
            agent = Agent(
                name=DEMO_AGENT_NAME,
                server_name=DEMO_SERVER_NAME,
                hostname="demo-host",
                ip_address="127.0.0.1",
                log_path=str(LOG_PATH),
                token_hash=token_hash,
                status="active"
            )
            session.add(agent)
            session.commit()
            session.refresh(agent)
            print(f"Created demo agent with ID: {agent.id}")
        else:
            print(f"Demo agent already exists with ID: {agent.id}")
            # Ensure the token hash matches our known token
            agent.token_hash = security.get_password_hash(DEMO_TOKEN)
            session.commit()
            
        # Write config.yml automatically
        config_content = f"""agent_id: "{agent.id}"
agent_token: "{DEMO_TOKEN}"
server_url: "http://localhost:8000"
log_path: "{LOG_PATH}"
batch_size: 5
flush_interval_seconds: 2
offset_file: "{AGENT_DIR / 'agent.offset'}"
debug: true
"""
        with open(CONFIG_PATH, "w") as f:
            f.write(config_content)
        print(f"Successfully generated agent config: {CONFIG_PATH}")
        return agent.id
    except Exception as e:
        print(f"Error registering agent: {e}")
        sys.exit(1)
    finally:
        session.close()

# List of dummy endpoints, methods, IPs, User Agents
ENDPOINTS = [
    ("/v1/forecast", "GET"),
    ("/api/auth/login", "POST"),
    ("/api/dashboard/overview", "GET"),
    ("/api/users", "GET"),
    ("/api/agents", "POST"),
    ("/static/js/main.js", "GET"),
    ("/static/css/styles.css", "GET"),
    ("/index.html", "GET"),
    ("/api/ws/realtime", "GET"),
]

ERROR_ENDPOINTS = [
    ("/wp-admin", "GET"),
    ("/admin", "GET"),
    ("/api/users/delete/all", "POST"),
    ("/api/reports/heavy-error", "GET"),
    ("/.env", "GET"),
]

SLOW_ENDPOINTS = [
    ("/api/reports/heavy", "GET"),
    ("/api/logs?limit=5000", "GET"),
    ("/api/dashboard/status-timeseries", "GET"),
]

IPS = [
    "123.24.206.56", "172.71.210.188", "162.158.193.41", 
    "162.158.193.40", "172.68.211.205", "162.158.243.100",
    "192.168.1.50", "8.8.8.8", "1.1.1.1"
]

HOSTS = [
    ("https", DEMO_SERVER_NAME),
    ("http", DEMO_SERVER_NAME),
    ("https", "api.zero9vn.com"),
    ("http", "admin.zero9vn.com")
]

USER_AGENTS = [
    "okhttp/5.3.2", "PostmanRuntime/7.37.3", 
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/605.1.15"
]

def generate_log_line():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))) # ICT time zone
    time_str = now.strftime("%Y-%m-%dT%H:%M:%S+07:00")
    
    # 80% success, 10% slow, 10% error
    rand = random.random()
    
    real_ip = random.choice(IPS)
    remote = random.choice(IPS)
    user_agent = random.choice(USER_AGENTS)
    
    if rand < 0.80:
        # Success
        uri, method = random.choice(ENDPOINTS)
        status = random.choice([200, 200, 200, 200, 201, 301, 302])
        body_bytes = random.randint(100, 5000)
        request_time = round(random.uniform(0.002, 0.080), 3)
        upstream_response_time = round(request_time - random.uniform(0.001, 0.003), 3)
        upstream_addr = "127.0.0.1:8080" if random.random() > 0.1 else "-"
    elif rand < 0.90:
        # Slow Requests
        uri, method = random.choice(SLOW_ENDPOINTS)
        status = 200
        body_bytes = random.randint(50000, 250000)
        request_time = round(random.uniform(settings.SLOW_REQUEST_THRESHOLD_SECONDS + 0.1, 4.5), 3)
        upstream_response_time = round(request_time - random.uniform(0.005, 0.020), 3)
        upstream_addr = "127.0.0.1:8080"
    else:
        # Errors
        uri, method = random.choice(ERROR_ENDPOINTS)
        status = random.choice([400, 401, 403, 404, 500, 503])
        body_bytes = random.randint(20, 1000)
        request_time = round(random.uniform(0.005, 0.150), 3)
        upstream_response_time = round(request_time - random.uniform(0.001, 0.005), 3) if status >= 500 else "-"
        upstream_addr = "127.0.0.1:8080" if status >= 500 else "-"

    if upstream_response_time == "-":
        upstream_time_val = "-"
    else:
        upstream_time_val = str(max(0.0, upstream_response_time))

    scheme, host = random.choice(HOSTS)
    
    log_entry = {
        "time": time_str,
        "real_ip": real_ip,
        "remote": remote,
        "cf_ip": real_ip,
        "xff": real_ip,
        "user": "meteo_user" if random.random() > 0.3 else "-",
        "scheme": scheme,
        "host": host,
        "method": method,
        "uri": uri,
        "args": f"rand={random.randint(1,100)}" if "?" not in uri else "",
        "request": f"{method} {uri} HTTP/2.0",
        "status": status,
        "body_bytes": body_bytes,
        "http_ref": "https://zero9vn.com/" if random.random() > 0.5 else "-",
        "agent": user_agent,
        "request_time": request_time,
        "upstream_response_time": upstream_time_val,
        "upstream_addr": upstream_addr
    }
    
    return log_entry

def push_directly(agent_id, count=50):
    url = f"http://localhost:8000/api/ingest/nginx"
    headers = {
        "X-Agent-Id": str(agent_id),
        "X-Agent-Token": DEMO_TOKEN,
        "Content-Type": "application/json"
    }
    
    print(f"\nGenerating and pushing {count} dummy logs directly to {url}...")
    logs = [generate_log_line() for _ in range(count)]
    
    payload = {
        "agent_id": str(agent_id),
        "server_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "logs": logs
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        print(f"Successfully pushed directly! Response: {resp.json()}")
    except Exception as e:
        print(f"Failed to push directly: {e}")

def main():
    agent_id = register_agent()
    
    # Support non-interactive mode via command line argument or non-TTY
    choice = "3" # Default
    if len(sys.argv) > 1:
        choice = sys.argv[1].strip()
    elif not sys.stdin.isatty():
        # Read from stdin if piped
        try:
            piped_input = sys.stdin.read().strip()
            if piped_input in ["1", "2", "3"]:
                choice = piped_input
        except Exception:
            pass
    else:
        try:
            print("\n" + "="*50)
            print(" DUMMY DATA GENERATOR FOR NGINX MONITORING ")
            print("="*50)
            print("1. Write dummy logs to simulated file (For ./agent run tailing test)")
            print("2. Direct push dummy logs to backend via HTTP API")
            print("3. Both (Write to file AND push directly)")
            print("="*50)
            choice = input("Enter your choice (1/2/3): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            return

    if choice not in ["1", "2", "3"]:
        print("Invalid choice, defaulting to Option 3.")
        choice = "3"
        
    if choice in ["2", "3"]:
        push_directly(agent_id, count=100)
        
    if choice in ["1", "3"]:
        print(f"\nWriting live dummy logs to {LOG_PATH}...")
        print("Press Ctrl+C to stop.\n")
        
        # Touch file
        with open(LOG_PATH, "a") as f:
            pass
            
        success_count = 0
        slow_count = 0
        error_count = 0
        
        try:
            while True:
                log_entry = generate_log_line()
                
                if choice in ["1", "3"]:
                    # Write to file
                    with open(LOG_PATH, "a") as f:
                        f.write(json.dumps(log_entry) + "\n")
                        
                if choice in ["2", "3"]:
                    # Push directly every single log (or we can just call push_directly with count=1)
                    try:
                        url = f"http://localhost:8000/api/ingest/nginx"
                        headers = {
                            "X-Agent-Id": str(agent_id),
                            "X-Agent-Token": DEMO_TOKEN,
                            "Content-Type": "application/json"
                        }
                        payload = {
                            "agent_id": str(agent_id),
                            "server_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            "logs": [log_entry]
                        }
                        requests.post(url, headers=headers, json=payload, timeout=5)
                    except Exception:
                        pass
                
                # Stats console printing
                status = log_entry["status"]
                req_time = log_entry["request_time"]
                uri = log_entry["uri"]
                
                if status >= 400:
                    status_color = "\033[91m" # Red
                    error_count += 1
                elif req_time >= settings.SLOW_REQUEST_THRESHOLD_SECONDS:
                    status_color = "\033[93m" # Yellow
                    slow_count += 1
                else:
                    status_color = "\033[92m" # Green
                    success_count += 1
                    
                print(f"[{log_entry['time']}] {log_entry['method']} {uri} -> {status_color}{status}\033[0m ({req_time}s) | Success: {success_count}, Slow: {slow_count}, Error: {error_count}")
                
                time.sleep(random.uniform(0.3, 1.5))
        except KeyboardInterrupt:
            print("\nStopped writing logs to file.")

if __name__ == "__main__":
    main()
