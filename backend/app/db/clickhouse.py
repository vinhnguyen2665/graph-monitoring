import clickhouse_connect
from app.core.config import settings

def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_PORT,
        username=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD,
        database=settings.CLICKHOUSE_DB if settings.CLICKHOUSE_DB else 'default'
    )

def init_clickhouse_schema():
    # Connect to default DB first to create our monitoring DB
    client = clickhouse_connect.get_client(
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_PORT,
        username=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD
    )
    
    db_name = settings.CLICKHOUSE_DB
    client.command(f'CREATE DATABASE IF NOT EXISTS {db_name}')
    
    # Reconnect to the specific DB
    client = get_clickhouse_client()
    
    # 1. Nginx Access Logs table
    client.command(f'''
    CREATE TABLE IF NOT EXISTS {db_name}.nginx_access_logs
    (
        ts DateTime64(3, 'UTC'),
        date Date MATERIALIZED toDate(ts),

        agent_id String,
        server_name LowCardinality(String),

        real_ip String,
        remote String,
        cf_ip String,
        xff String,

        nginx_user String,
        scheme LowCardinality(String),
        host LowCardinality(String),

        method LowCardinality(String),
        uri String,
        args String,
        request String,
        protocol LowCardinality(String),

        status UInt16,
        status_class LowCardinality(String),

        body_bytes UInt64,

        http_ref String,
        user_agent String,

        request_time Float64,
        upstream_response_time Float64,
        upstream_addr String,

        is_error UInt8,
        is_slow UInt8,

        ingest_time DateTime64(3, 'UTC') DEFAULT now64(3),
        
        INDEX idx_uri uri TYPE tokenbf_v1(32768, 3, 0) GRANULARITY 4,
        INDEX idx_real_ip real_ip TYPE bloom_filter(0.01) GRANULARITY 4,
        INDEX idx_upstream upstream_addr TYPE bloom_filter(0.01) GRANULARITY 4
    )
    ENGINE = MergeTree
    PARTITION BY toYYYYMM(date)
    ORDER BY (agent_id, host, ts, status, uri)
    TTL date + INTERVAL 180 DAY
    SETTINGS index_granularity = 8192;
    ''')

    # 2. Materialized View Metrics 1M
    client.command(f'''
    CREATE TABLE IF NOT EXISTS {db_name}.nginx_metrics_1m
    (
        bucket DateTime('UTC'),
        agent_id String,
        server_name LowCardinality(String),
        host LowCardinality(String),
        method LowCardinality(String),
        status_class LowCardinality(String),
        upstream_addr String,

        requests UInt64,
        errors UInt64,
        slow_requests UInt64,
        bytes UInt64,
        avg_request_time Float64,
        p95_request_time Float64,
        p99_request_time Float64
    )
    ENGINE = SummingMergeTree
    PARTITION BY toYYYYMM(bucket)
    ORDER BY (agent_id, host, bucket, status_class, upstream_addr);
    ''')
    
    print("ClickHouse schema initialized successfully.")

if __name__ == "__main__":
    init_clickhouse_schema()
