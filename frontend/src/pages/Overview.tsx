import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Typography } from 'antd';
import { api } from '../api/axios';
import { Area, Column } from '@ant-design/plots';
import { useTranslation } from '../i18n/LanguageContext';

const { Title } = Typography;

export const Overview: React.FC = () => {
  const [stats, setStats] = useState<any>({});
  const [requestTimeseries, setRequestTimeseries] = useState([]);
  const [statusTimeseries, setStatusTimeseries] = useState([]);
  const { t } = useTranslation();

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [overviewRes, reqRes, statusRes] = await Promise.all([
        api.get('/dashboard/overview'),
        api.get('/dashboard/request-timeseries'),
        api.get('/dashboard/status-timeseries')
      ]);
      setStats(overviewRes?.data || {});
      setRequestTimeseries(Array.isArray(reqRes?.data) ? reqRes.data : []);
      setStatusTimeseries(Array.isArray(statusRes?.data) ? statusRes.data : []);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>{t('overview')}</Title>
      
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic title={t('totalRequests')} value={stats.total_requests || 0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title={t('errorRate')} value={stats.total_errors || 0} styles={{ content: { color: '#cf1322' } }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title={t('slowRequests')} value={stats.total_slow || 0} styles={{ content: { color: '#faad14' } }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title={`${t('avgLatency')} (s)`} value={stats.avg_latency ? stats.avg_latency.toFixed(3) : 0} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={16}>
          <Card title={t('reqTrend')}>
            <Area 
              data={requestTimeseries} 
              xField="time_bucket" 
              yField="count" 
              smooth={true}
              height={300}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title={t('statusDist')}>
            <Column 
              data={statusTimeseries} 
              xField="status_class" 
              yField="count"
              colorField="status_class"
              height={300}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};
