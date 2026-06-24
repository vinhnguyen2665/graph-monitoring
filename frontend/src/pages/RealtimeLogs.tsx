import React, { useEffect, useState, useRef } from 'react';
import { Table, Tag, Card, Button, Space, Typography } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined, ClearOutlined } from '@ant-design/icons';
import { useTranslation } from '../i18n/LanguageContext';

const { Title } = Typography;

export const RealtimeLogs: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [isPaused, setIsPaused] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const { t } = useTranslation();

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    ws.current = new WebSocket('ws://localhost:8000/api/ws/realtime');
    
    ws.current.onmessage = (event) => {
      if (isPaused) return;
      
      try {
        const data = JSON.parse(event.data);
        setLogs((prevLogs) => [data, ...prevLogs].slice(0, 100)); // Keep last 100
      } catch (e) {
        console.error("Invalid WS message", e);
      }
    };
  };

  useEffect(() => {
    // If we toggle play/pause we need to update the closure or just rely on state
    // But since onmessage is set once, we need to handle isPaused inside
    if (ws.current) {
      ws.current.onmessage = (event) => {
        if (isPaused) return;
        try {
          const data = JSON.parse(event.data);
          setLogs((prevLogs) => [data, ...prevLogs].slice(0, 100));
        } catch (e) {
          console.error("Invalid WS message", e);
        }
      };
    }
  }, [isPaused]);

  const columns = [
    { title: t('time'), dataIndex: 'ts', key: 'ts', width: 200 },
    { title: t('clientIp'), dataIndex: 'real_ip', key: 'real_ip' },
    { title: t('method'), dataIndex: 'method', key: 'method', width: 100 },
    { title: t('address'), dataIndex: 'server_name', key: 'server_name' },
    { title: t('uri'), dataIndex: 'uri', key: 'uri', ellipsis: true },
    { 
      title: t('status'), 
      dataIndex: 'status', 
      key: 'status',
      render: (status: number) => {
        let color = 'green';
        if (status >= 400 && status < 500) color = 'orange';
        if (status >= 500) color = 'red';
        return <Tag color={color}>{status}</Tag>;
      }
    },
    { title: t('duration'), dataIndex: 'request_time', key: 'request_time' },
    { title: t('upstream'), dataIndex: 'destination', key: 'destination' },
  ];

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={2} style={{ margin: 0 }}>{t('realtimeLogs')}</Title>
        <Space>
          <Button 
            type={isPaused ? "primary" : "default"}
            icon={isPaused ? <PlayCircleOutlined /> : <PauseCircleOutlined />}
            onClick={() => setIsPaused(!isPaused)}
          >
            {isPaused ? t('play') : t('pause')}
          </Button>
          <Button icon={<ClearOutlined />} onClick={() => setLogs([])}>
            {t('clear')}
          </Button>
        </Space>
      </div>

      <Card styles={{ body: { padding: 0 } }}>
        <Table 
          columns={columns} 
          dataSource={logs} 
          rowKey={(record) => record.ts + Math.random()}
          pagination={false}
          size="small"
        />
      </Card>
    </div>
  );
};
