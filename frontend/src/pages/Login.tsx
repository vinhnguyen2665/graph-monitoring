import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, Select, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { api } from '../api/axios';
import { useTranslation } from '../i18n/LanguageContext';
import type { Language } from '../i18n/translations';

const { Title } = Typography;

export const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  const { t, language, setLanguage } = useTranslation();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('username', values.email);
      formData.append('password', values.password);

      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const { access_token, refresh_token } = response.data;
      
      // Fetch user profile
      const userResponse = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      
      setAuth(userResponse.data, access_token, refresh_token);
      message.success('Login successful');
      navigate('/');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f0f2f5', position: 'relative' }}>
      <div style={{ position: 'absolute', top: 24, right: 24 }}>
        <Select 
          value={language} 
          onChange={(lang) => setLanguage(lang as Language)} 
          style={{ width: 140 }}
          options={[
            { value: 'en', label: '🇬🇧 English' },
            { value: 'vi', label: '🇻🇳 Tiếng Việt' },
            { value: 'ja', label: '🇯🇵 日本語' }
          ]}
        />
      </div>
      <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2}>Nginx Monitor</Title>
          <p>{t('loginSub')}</p>
        </div>
        
        <Form
          name="normal_login"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          layout="vertical"
        >
          <Form.Item
            name="email"
            rules={[{ required: true, message: t('usernameReq') }, { type: 'email', message: 'Invalid email format' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="Email" size="large" />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: t('passwordReq') }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder={t('password')}
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" style={{ width: '100%' }} size="large" loading={loading}>
              {t('loginTitle')}
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};
