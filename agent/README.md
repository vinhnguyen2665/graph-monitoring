# Nginx Monitor - Python Stateful Ingestion Agent

A lightweight, reliable, and asynchronous Python log shipping agent. It tails active Nginx JSON access log files and transmits them in structured batches to the FastAPI backend.

## 🛠️ Key Features
* **Stateful Tailing (Byte Offset Persistence)**: Remembers its exact reading position (`offset`) in the log file, saving state to `agent.offset`. If the agent restarts or the network drops, it resumes from the last successfully read line, preventing duplicates or log data loss.
* **Log Rotation Detection**: Automatically handles log rotations (truncation or replacement) by comparing file sizes and resetting the offset index as needed.
* **Smart Buffering & Batching**: Buffers logs and flushes them either when a batch limit is hit (e.g., 100 logs) or when a duration threshold is reached (e.g., every 3 seconds).
* **Robust Exception Handling**: Automatically filters invalid JSON lines, warns on decoding issues, and retries on connection failures.

---

## 🚀 Setup & Execution

### 1. Install Dependencies
Make sure you have installed the required Python dependencies:
```bash
cd agent
pip install -r requirements.txt
```

### 2. Configure the Agent (`config.yml`)
The agent loads its credentials and target log file paths from a `config.yml` file in the same directory.
Example configuration (`config.yml.example`):
```yaml
agent_id: "agent-uuid-from-postgres"
agent_token: "agent-secret-token"
server_url: "http://localhost:8000"
log_path: "/var/log/nginx/access_json.log"
batch_size: 100
flush_interval_seconds: 3
offset_file: "./agent.offset"
debug: true
```

### 3. Run the Agent
To start tailing and pushing logs:
```bash
python agent.py run --config config.yml
```

To test the connection to the backend health check API:
```bash
python agent.py test --config config.yml
```

To validate that your Nginx log file is writing correct JSON strings:
```bash
python agent.py validate-log --file /var/log/nginx/access_json.log
```

---

## 🧪 Simulated Dummy Data Generator (`generate_dummy_logs.py`)

For local testing and validation without setting up a real Nginx server, a powerful simulated log generator is provided in the `agent/` folder.

To run the generator:
```bash
python generate_dummy_logs.py
```

### Modes of Operation:
Upon launching, the script offers 3 modes:
1. **Option 1 (Simulated Tailing File)**: Continuously writes randomized, highly realistic Nginx logs (80% Success, 10% Errors, 10% Slow Requests) into `agent/dummy_access.log`. You can tail this file by running the actual `agent.py` in another terminal!
2. **Option 2 (Direct Push via HTTP API)**: Directly bundles and ships a batch of 100 logs straight to the backend `/api/ingest/nginx` endpoint. Great for instantly populating dashboards with graphs and alerts!
3. **Option 3 (Both)**: Runs a direct push of 100 logs AND starts streaming logs to `dummy_access.log` simultaneously.

### Non-Interactive Command-Line Execution
Perfect for background execution or automation:
```bash
# Push 100 logs directly
python generate_dummy_logs.py 2

# Continuous background streaming to log file
python generate_dummy_logs.py 1 > /dev/null 2>&1 &
```
