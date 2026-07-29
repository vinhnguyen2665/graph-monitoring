import datetime
import glob
import hashlib
import json
import logging
import os
import platform
import re
import socket
import time
import uuid

import click
import requests
import yaml


def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s [%(levelname)s] %(message)s')


def load_offsets(offset_file):
    if os.path.exists(offset_file):
        with open(offset_file, 'r') as f:
            try:
                content = f.read().strip()
                if content.startswith('{'):
                    return json.loads(content)
                else:
                    # Fallback for old single offset format
                    return {}
            except Exception:
                return {}
    return {}


def save_offsets(offset_file, offsets):
    try:
        with open(offset_file, 'w') as f:
            json.dump(offsets, f)
    except Exception as e:
        logging.error(f"Failed to save offsets to {offset_file}: {e}")


def find_files(patterns):
    if not isinstance(patterns, list):
        patterns = [patterns]
    
    matched_files = set()
    for pattern in patterns:
        # 1. Try glob first
        glob_matches = glob.glob(pattern)
        if glob_matches:
            for f in glob_matches:
                if os.path.isfile(f):
                    matched_files.add(os.path.abspath(f))
            continue
            
        # 2. Try regex
        norm_pattern = os.path.normpath(pattern)
        dir_name = os.path.dirname(norm_pattern)
        file_pattern = os.path.basename(norm_pattern)
        
        if not dir_name:
            dir_name = '.'
            
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            try:
                regex = re.compile(file_pattern)
                for entry in os.listdir(dir_name):
                    full_path = os.path.join(dir_name, entry)
                    if os.path.isfile(full_path) and regex.search(entry):
                        matched_files.add(os.path.abspath(full_path))
            except re.error as e:
                logging.error(f"Invalid regex pattern {file_pattern}: {e}")
                
        # 3. Direct check
        if os.path.isfile(pattern):
            matched_files.add(os.path.abspath(pattern))
            
    return sorted(list(matched_files))


def update_tracked_files(patterns, open_files, file_offsets):
    current_files = find_files(patterns)
    
    # Close and remove files that are no longer matched or existing
    for path in list(open_files.keys()):
        if path not in current_files or not os.path.exists(path):
            logging.info(f"File {path} is no longer matched or exists. Closing handle.")
            try:
                open_files[path].close()
            except Exception:
                pass
            open_files.pop(path)
            
    # Open new files
    for path in current_files:
        if path not in open_files:
            try:
                f = open(path, 'r')
                offset = file_offsets.get(path, 0)
                try:
                    size = os.path.getsize(path)
                    if offset > size:
                        logging.info(f"Offset for new tracked file {path} ({offset}) is greater than size ({size}). Resetting to 0.")
                        offset = 0
                except OSError:
                    offset = 0
                
                f.seek(offset)
                open_files[path] = f
                file_offsets[path] = offset
                logging.info(f"Now tracking {path} at offset {offset}")
            except Exception as e:
                logging.error(f"Failed to open file {path}: {e}")


def fix_json_string(line):
    # Common issue: trailing comma before closing brace
    line = line.strip()
    if line.endswith(',}'):
        line = line[:-2] + '}'
    return line


def get_system_fingerprint():
    """Generates a stable hardware/system fingerprint based on MAC address, hostname, and OS platform."""
    mac = uuid.getnode()
    host = socket.gethostname()
    plat = platform.platform()
    raw = f"{mac}-{host}-{plat}".encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def save_config(config_file, config_data):
    """Saves updated configuration back to the YAML file."""
    try:
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        logging.info(f"Updated configuration saved to {config_file}")
    except Exception as e:
        logging.error(f"Failed to save config to {config_file}: {e}")


def register_agent(config, config_file):
    """Auto-registers the agent with the backend using system fingerprint."""
    server_url = config.get('server_url', 'http://localhost:8000').rstrip('/')
    url = f"{server_url}/api/agents/register"

    hostname = socket.gethostname()
    server_name = config.get('server_name') or hostname
    fingerprint = get_system_fingerprint()

    # Determine local IP address if possible
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except Exception:
        ip_address = "127.0.0.1"

    log_paths = config.get('log_path', [])
    log_path_str = ", ".join(log_paths) if isinstance(log_paths, list) else str(log_paths)

    payload = {
        "server_name": server_name,
        "name": f"Agent-{hostname}",
        "hostname": hostname,
        "ip_address": ip_address,
        "log_path": log_path_str,
        "fingerprint": fingerprint
    }

    logging.info(f"Auto-registering agent with server {url} (Fingerprint: {fingerprint[:8]}...)...")

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        config['agent_id'] = str(data['agent_id'])
        config['agent_token'] = data['agent_token']
        if 'server_name' not in config:
            config['server_name'] = server_name

        save_config(config_file, config)
        logging.info(f"Agent registration successful ({data.get('status')})! Agent ID: {data['agent_id']}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Agent registration failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Server response: {e.response.text}")
        return False


def ensure_agent_credentials(config, config_file):
    """Ensures agent has valid credentials; auto-registers if missing."""
    if not config.get('agent_id') or not config.get('agent_token'):
        logging.info("Agent credentials missing in config. Triggering auto-registration...")
        if not register_agent(config, config_file):
            raise RuntimeError("Auto-registration failed. Cannot proceed without valid agent credentials.")


def send_batch(config, config_file, batch):
    url = f"{config['server_url'].rstrip('/')}/api/ingest/nginx"
    headers = {
        "X-Agent-Id": str(config.get('agent_id', '')),
        "X-Agent-Token": str(config.get('agent_token', '')),
        "Content-Type": "application/json"
    }
    payload = {
        "agent_id": str(config.get('agent_id', '')),
        "server_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "logs": batch
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 401:
            logging.warning("Received 401 Unauthorized from backend. Re-registering agent...")
            if register_agent(config, config_file):
                headers["X-Agent-Id"] = str(config['agent_id'])
                headers["X-Agent-Token"] = str(config['agent_token'])
                payload["agent_id"] = str(config['agent_id'])
                resp = requests.post(url, headers=headers, json=payload, timeout=10)

        resp.raise_for_status()
        logging.info(f"Successfully sent batch of {len(batch)} logs. Response: {resp.json()}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send batch: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Server response: {e.response.text}")
        return False


@click.group()
def cli():
    """Nginx Log Monitoring Agent"""
    pass


@cli.command()
@click.option('--config', default='config.yml', help='Path to config file')
def run(config):
    """Run the agent to tail logs"""
    cfg = load_config(config)
    setup_logging(cfg.get('debug', False))
    ensure_agent_credentials(cfg, config)

    log_path = cfg['log_path']
    offset_file = cfg.get('offset_file', 'agent.offset')
    batch_size = cfg.get('batch_size', 100)
    flush_interval = cfg.get('flush_interval_seconds', 3)

    file_offsets = load_offsets(offset_file)
    open_files = {}

    update_tracked_files(log_path, open_files, file_offsets)
    if not open_files:
        logging.warning(f"No log files found matching pattern(s): {log_path}")

    logging.info(f"Starting agent. Tailing matching files from log_path: {log_path}")

    batch = []
    last_flush = time.time()
    last_file_scan = time.time()
    scan_interval = 10.0  # seconds

    try:
        while True:
            # Periodically scan for file changes
            if time.time() - last_file_scan >= scan_interval:
                update_tracked_files(log_path, open_files, file_offsets)
                last_file_scan = time.time()

            any_lines_read = False
            for path, f in list(open_files.items()):
                while len(batch) < batch_size:
                    current_pos = f.tell()
                    line = f.readline()
                    if not line:
                        # Handle log rotation
                        try:
                            if os.path.exists(path) and os.path.getsize(path) < current_pos:
                                logging.info(f"Log file {path} truncated/rotated. Resetting offset.")
                                f.seek(0)
                                file_offsets[path] = 0
                                any_lines_read = True
                                continue
                        except OSError:
                            pass
                        break

                    any_lines_read = True
                    line = fix_json_string(line)
                    try:
                        log_obj = json.loads(line)
                        batch.append(log_obj)
                        file_offsets[path] = f.tell()
                    except json.JSONDecodeError:
                        logging.warning(f"Invalid JSON at offset {current_pos} in {path}: {line}")
                        file_offsets[path] = f.tell()

                    if len(batch) >= batch_size:
                        if send_batch(cfg, config, batch):
                            save_offsets(offset_file, file_offsets)
                            batch = []
                            last_flush = time.time()
                        else:
                            logging.info("Sleeping before retry...")
                            time.sleep(5)

            if not any_lines_read:
                # Time to flush?
                if batch and (time.time() - last_flush) >= flush_interval:
                    if send_batch(cfg, config, batch):
                        save_offsets(offset_file, file_offsets)
                        batch = []
                        last_flush = time.time()
                time.sleep(0.5)

    finally:
        for path, f in open_files.items():
            try:
                f.close()
            except Exception:
                pass


@cli.command()
@click.option('--config', default='config.yml', help='Path to config file')
def test(config):
    """Test connection to the server"""
    cfg = load_config(config)
    setup_logging(cfg.get('debug', False))

    url = f"{cfg['server_url'].rstrip('/')}/api/health"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        logging.info(f"Successfully connected to {url}. Server status: {resp.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to connect to server: {e}")


@cli.command()
@click.option('--file', required=True, help='Path or pattern of log files to validate')
def validate_log(file):
    """Validate log format"""
    setup_logging(True)
    
    files = find_files(file)
    if not files:
        logging.error(f"No files matching path/pattern found: {file}")
        return

    for path in files:
        logging.info(f"Validating file: {path}")
        valid = 0
        invalid = 0
        try:
            with open(path, 'r') as f:
                for i, line in enumerate(f):
                    try:
                        line = fix_json_string(line)
                        json.loads(line)
                        valid += 1
                    except json.JSONDecodeError as e:
                        logging.error(f"Line {i + 1} in {path} is invalid JSON: {e}")
                        invalid += 1
            logging.info(f"Validation complete for {path}. Valid lines: {valid}, Invalid lines: {invalid}")
        except Exception as e:
            logging.error(f"Failed to read file {path}: {e}")



if __name__ == '__main__':
    cli()
