import datetime
import json
import logging
import os
import time

import click
import requests
import yaml


def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s [%(levelname)s] %(message)s')


def get_offset(offset_file):
    if os.path.exists(offset_file):
        with open(offset_file, 'r') as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 0
    return 0


def save_offset(offset_file, offset):
    with open(offset_file, 'w') as f:
        f.write(str(offset))


def fix_json_string(line):
    # Common issue: trailing comma before closing brace
    line = line.strip()
    if line.endswith(',}'):
        line = line[:-2] + '}'
    return line


def send_batch(config, batch):
    url = f"{config['server_url'].rstrip('/')}/api/ingest/nginx"
    headers = {
        "X-Agent-Id": config['agent_id'],
        "X-Agent-Token": config['agent_token'],
        "Content-Type": "application/json"
    }
    payload = {
        "agent_id": config['agent_id'],
        "server_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "logs": batch
    }

    try:
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

    log_path = cfg['log_path']
    offset_file = cfg.get('offset_file', 'agent.offset')
    batch_size = cfg.get('batch_size', 100)
    flush_interval = cfg.get('flush_interval_seconds', 3)

    if not os.path.exists(log_path):
        logging.error(f"Log file not found: {log_path}")
        return

    offset = get_offset(offset_file)
    logging.info(f"Starting agent. Tailing {log_path} from offset {offset}")

    batch = []
    last_flush = time.time()

    with open(log_path, 'r') as f:
        f.seek(offset)

        while True:
            current_pos = f.tell()
            line = f.readline()

            if not line:
                # Handle log rotation
                if os.path.exists(log_path):
                    if os.path.getsize(log_path) < current_pos:
                        logging.info("Log file truncated/rotated. Resetting offset.")
                        f.seek(0)
                        save_offset(offset_file, 0)
                        continue

                # Time to flush?
                if batch and (time.time() - last_flush) >= flush_interval:
                    if send_batch(cfg, batch):
                        save_offset(offset_file, current_pos)
                        batch = []
                        last_flush = time.time()

                time.sleep(0.5)
                continue

            # Parse line
            line = fix_json_string(line)
            try:
                log_obj = json.loads(line)
                batch.append(log_obj)
            except json.JSONDecodeError:
                logging.warning(f"Invalid JSON at offset {current_pos}: {line}")

            # Batch full?
            if len(batch) >= batch_size:
                if send_batch(cfg, batch):
                    save_offset(offset_file, f.tell())
                    batch = []
                    last_flush = time.time()
                else:
                    # Exponential backoff or sleep on failure
                    logging.info("Sleeping before retry...")
                    time.sleep(5)
                    # We don't advance the file pointer or offset if it fails
                    # actually we did advance the file pointer, but offset is not saved.
                    # This means on restart it will resend. If it keeps running it will lose logs 
                    # unless we keep retrying. For simplicity, we just retry next loop
                    # but wait, batch is not cleared. So it will retry sending same batch.


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
@click.option('--file', required=True, help='Path to log file to validate')
def validate_log(file):
    """Validate log format"""
    setup_logging(True)
    if not os.path.exists(file):
        logging.error("File not found")
        return

    valid = 0
    invalid = 0
    with open(file, 'r') as f:
        for i, line in enumerate(f):
            try:
                line = fix_json_string(line)
                json.loads(line)
                valid += 1
            except json.JSONDecodeError as e:
                logging.error(f"Line {i + 1} is invalid JSON: {e}")
                invalid += 1

    logging.info(f"Validation complete. Valid lines: {valid}, Invalid lines: {invalid}")


if __name__ == '__main__':
    cli()
