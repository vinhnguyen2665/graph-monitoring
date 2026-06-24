import React from 'react';
import { Layout, Menu, Button, Select } from 'antd';
import {
  DashboardOutlined,
  ThunderboltOutlined,
  NodeIndexOutlined,
  WarningOutlined,
  ClockCircleOutlined,
  AlertOutlined,
  UserOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useTranslation } from '../i18n/LanguageContext';
import type { Language } from '../i18n/translations';

const { Header, Content, Sider } = Layout;

export const DashboardLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const logout = useAuthStore((state) => state.logout);
  const currentUser = useAuthStore((state) => state.user);
  const { t, language, setLanguage } = useTranslation();

  const menuItems = [
    { key: '/', icon: <DashboardOutlined />, label: t('overview') },
    { key: '/realtime', icon: <ThunderboltOutlined />, label: t('realtimeLogs') },
    { key: '/topology', icon: <NodeIndexOutlined />, label: t('topology') },
    { key: '/errors', icon: <WarningOutlined />, label: t('errors') },
    { key: '/slow-requests', icon: <ClockCircleOutlined />, label: t('slowRequests') },
    { key: '/alerts', icon: <AlertOutlined />, label: t('alerts') },
  ];

  if (currentUser?.role === 'admin') {
    menuItems.push({ key: '/users', icon: <UserOutlined />, label: t('users') });
  }

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible theme="dark">
        <div style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)', borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 'bold' }}>
          Nginx Monitor
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          onClick={({ key }) => navigate(key)}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 1px 4px rgba(0,21,41,.08)' }}>
          <div>
            <strong>{t('welcome')}:</strong> {currentUser?.username || 'Guest'} ({currentUser?.role})
          </div>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <Select 
              value={language} 
              onChange={(lang) => setLanguage(lang as Language)} 
              style={{ width: 140, marginRight: 16 }}
              options={[
                { value: 'en', label: '🇬🇧 English' },
                { value: 'vi', label: '🇻🇳 Tiếng Việt' },
                { value: 'ja', label: '🇯🇵 日本語' }
              ]}
            />
            <Button type="text" icon={<LogoutOutlined />} onClick={handleLogout}>
              {t('logout')}
            </Button>
          </div>
        </Header>
        <Content style={{ margin: 0, overflow: 'initial', background: '#fff', minHeight: 'calc(100vh - 64px)' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};
