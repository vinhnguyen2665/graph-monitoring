import React, { useEffect, useState } from 'react';
import { Table, Card, Tag, Typography, message } from 'antd';
import { api } from '../api/axios';
import { useTranslation } from '../i18n/LanguageContext';

const { Title } = Typography;

export const ErrorMonitoring: React.FC = () => {
  const [errorLogs, setErrorLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [total, setTotal] = useState(0);
  const { t } = useTranslation();

  useEffect(() => {
    fetchErrors(currentPage, pageSize);
    const interval = setInterval(() => fetchErrors(currentPage, pageSize), 5000);
    return () => clearInterval(interval);
  }, [currentPage, pageSize]);

  const fetchErrors = async (page: number, size: number) => {
    setLoading(true);
    try {
      const limit = size;
      const offset = (page - 1) * size;
      const { data } = await api.get('/logs/errors', { params: { limit, offset } });
      setErrorLogs(data.data);
      setTotal(data.total || 0);
    } catch (e) {
      message.error("Failed to load errors");
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: t('time'), dataIndex: 'ts', key: 'ts' },
    { title: t('clientIp'), dataIndex: 'real_ip', key: 'real_ip' },
    { title: t('host'), dataIndex: 'host', key: 'host' },
    { title: t('method'), dataIndex: 'method', key: 'method' },
    { title: t('uri'), dataIndex: 'uri', key: 'uri', ellipsis: true },
    { 
      title: t('status'), 
      dataIndex: 'status', 
      key: 'status', 
      render: (status: number) => <Tag color="red">{status}</Tag> 
    },
    { title: t('duration'), dataIndex: 'request_time', key: 'request_time' }
  ];

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>{t('errorTitle')}</Title>
      <Card styles={{ body: { padding: 0 } }}>
        <Table 
          columns={columns} 
          dataSource={errorLogs} 
          rowKey={(record: any) => record.ts + Math.random()}
          loading={loading}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size);
            }
          }}
          size="middle"
        />
      </Card>
    </div>
  );
};
