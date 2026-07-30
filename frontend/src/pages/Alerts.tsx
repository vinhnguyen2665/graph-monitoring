import React, { useEffect, useState } from 'react';
import { Table, Card, Button, Modal, Form, Input, Select, Tag, Tabs, message } from 'antd';
import { api } from '../api/axios';
import { useTranslation } from '../i18n/LanguageContext';
import { formatClientTime } from '../utils/time';

const { TabPane } = Tabs;
const { Option } = Select;

export const Alerts: React.FC = () => {
  const [rules, setRules] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();
  const { t } = useTranslation();

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [rulesRes, eventsRes] = await Promise.all([
        api.get('/alerts/rules'),
        api.get('/alerts/events')
      ]);
      setRules(Array.isArray(rulesRes?.data) ? rulesRes.data : []);
      setEvents(Array.isArray(eventsRes?.data) ? eventsRes.data : []);
    } catch (e) {
      message.error(t('errResolve'));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRule = async (values: any) => {
    try {
      await api.post('/alerts/rules', values);
      message.success(t('succCreateRule'));
      setModalVisible(false);
      form.resetFields();
      fetchData();
    } catch (e) {
      message.error(t('errCreateRule'));
    }
  };

  const handleResolveEvent = async (eventId: string) => {
    try {
      await api.post(`/alerts/events/${eventId}/resolve`);
      message.success(t('succResolve'));
      fetchData();
    } catch (e) {
      message.error(t('errResolve'));
    }
  };

  const ruleColumns = [
    { title: t('ruleName'), dataIndex: 'name', key: 'name' },
    { 
      title: t('condition'), 
      dataIndex: 'condition_type', 
      key: 'condition_type',
      render: (type: string) => {
        let color = 'blue';
        let text = type;
        if (type === 'error_rate') { color = 'red'; text = t('condErrorRate'); }
        if (type === 'status_5xx_count') { color = 'volcano'; text = t('cond5xxCount'); }
        if (type === 'slow_request_count') { color = 'orange'; text = t('condSlowCount'); }
        if (type === 'ddos_attempt') { color = 'purple'; text = t('condDdos'); }
        if (type === 'scan_attempt') { color = 'magenta'; text = t('condScan'); }
        return <Tag color={color}>{text}</Tag>;
      }
    },
    { title: t('threshold'), dataIndex: 'threshold', key: 'threshold' },
    { title: t('durationMinutes'), dataIndex: 'duration_minutes', key: 'duration_minutes' },
    { 
      title: t('statusCol'), 
      dataIndex: 'enabled', 
      key: 'enabled',
      render: (enabled: boolean) => <Tag color={enabled ? "green" : "red"}>{enabled ? t('active') : t('disabled')}</Tag>
    }
  ];

  const eventColumns = [
    { title: t('time'), dataIndex: 'created_at', key: 'created_at', render: (val: string) => formatClientTime(val) },
    { title: t('ruleName'), dataIndex: 'rule_name', key: 'rule_name' },
    { 
      title: t('condition'), 
      dataIndex: 'event_type', 
      key: 'event_type',
      render: (type: string) => {
        let color = 'blue';
        let text = type;
        if (type === 'error_rate') { color = 'red'; text = t('condErrorRate'); }
        if (type === 'status_5xx_count') { color = 'volcano'; text = t('cond5xxCount'); }
        if (type === 'slow_request_count') { color = 'orange'; text = t('condSlowCount'); }
        if (type === 'ddos_attempt') { color = 'purple'; text = t('condDdos'); }
        if (type === 'scan_attempt') { color = 'magenta'; text = t('condScan'); }
        return <Tag color={color}>{text}</Tag>;
      }
    },
    { title: 'Value', dataIndex: 'value', key: 'value', render: (val: number) => val.toFixed(2) },
    { title: t('threshold'), dataIndex: 'threshold', key: 'threshold' },
    { title: t('details'), dataIndex: 'message', key: 'message' },
    { 
      title: t('statusCol'), 
      dataIndex: 'resolved', 
      key: 'resolved',
      render: (resolved: boolean) => <Tag color={resolved ? "green" : "red"}>{resolved ? t('resolved') : t('firing')}</Tag>
    },
    {
      title: t('actions'),
      key: 'action',
      render: (record: any) => (
        !record.resolved && (
          <Button type="primary" danger size="small" onClick={() => handleResolveEvent(record.id)}>
            {t('resolve')}
          </Button>
        )
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <h2>{t('alertsTitle')}</h2>
        <Button type="primary" onClick={() => setModalVisible(true)}>{t('createRule')}</Button>
      </div>

      <Tabs 
        defaultActiveKey="1"
        items={[
          {
            key: '1',
            label: t('activeEvents'),
            children: (
              <Card styles={{ body: { padding: 0 } }}>
                <Table columns={eventColumns} dataSource={events} rowKey="id" loading={loading} />
              </Card>
            )
          },
          {
            key: '2',
            label: t('alertRules'),
            children: (
              <Card styles={{ body: { padding: 0 } }}>
                <Table columns={ruleColumns} dataSource={rules} rowKey="id" loading={loading} />
              </Card>
            )
          }
        ]}
      />

      <Modal
        title={t('createRule')}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={handleCreateRule}>
          <Form.Item name="name" label={t('ruleName')} rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="condition_type" label={t('condition')} rules={[{ required: true }]}>
            <Select>
              <Option value="error_rate">{t('condErrorRate')}</Option>
              <Option value="status_5xx_count">{t('cond5xxCount')}</Option>
              <Option value="slow_request_count">{t('condSlowCount')}</Option>
              <Option value="ddos_attempt">{t('condDdos')}</Option>
              <Option value="scan_attempt">{t('condScan')}</Option>
            </Select>
          </Form.Item>
          <Form.Item name="threshold" label={t('threshold')} rules={[{ required: true }]}>
            <Input type="number" step="any" />
          </Form.Item>
          <Form.Item name="duration_minutes" label={t('durationMinutes')} initialValue={5}>
            <Input type="number" />
          </Form.Item>
          <Form.Item name="notification_channel" label={t('notificationChannel')} initialValue="console">
            <Select>
              <Option value="console">{t('console')}</Option>
              <Option value="webhook">{t('webhook')}</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};
