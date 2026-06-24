import React, { useEffect, useState } from 'react';
import { Table, Card, Button, Select, Space, Tag, message } from 'antd';
import { api } from '../api/axios';
import { useAuthStore } from '../store/authStore';
import { useTranslation } from '../i18n/LanguageContext';

const { Option } = Select;

export const Users: React.FC = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const currentUser = useAuthStore((state) => state.user);
  const { t } = useTranslation();

  useEffect(() => {
    if (currentUser?.role === 'admin') {
      fetchUsers();
    }
  }, [currentUser]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/users');
      setUsers(data);
    } catch (e) {
      message.error("Failed to fetch users");
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await api.put(`/users/${userId}/role`, { role: newRole });
      message.success("User role updated successfully");
      fetchUsers();
    } catch (e) {
      message.error("Failed to update user role");
    }
  };

  const handleDeleteUser = async (userId: string) => {
    try {
      await api.delete(`/users/${userId}`);
      message.success("User deleted successfully");
      fetchUsers();
    } catch (e) {
      message.error("Failed to delete user");
    }
  };

  if (currentUser?.role !== 'admin') {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <h2>Access Denied</h2>
        <p>You must be an administrator to view this page.</p>
      </div>
    );
  }

  const columns = [
    { title: t('username'), dataIndex: 'username', key: 'username' },
    { title: t('email'), dataIndex: 'email', key: 'email' },
    { title: t('fullName'), dataIndex: 'full_name', key: 'full_name' },
    { 
      title: t('role'), 
      dataIndex: 'role', 
      key: 'role',
      render: (role: string) => {
        let color = 'blue';
        let text = role.toUpperCase();
        if (role === 'admin') { color = 'red'; text = t('roleAdmin'); }
        if (role === 'operator') { color = 'orange'; text = t('roleOperator'); }
        if (role === 'viewer') { color = 'blue'; text = t('roleViewer'); }
        return <Tag color={color}>{text}</Tag>;
      }
    },
    {
      title: t('role'),
      key: 'change_role',
      render: (record: any) => (
        <Select 
          defaultValue={record.role} 
          style={{ width: 120 }} 
          onChange={(val) => handleRoleChange(record.id, val)}
          disabled={record.id === currentUser?.id}
        >
          <Option value="viewer">{t('roleViewer')}</Option>
          <Option value="operator">{t('roleOperator')}</Option>
          <Option value="admin">{t('roleAdmin')}</Option>
        </Select>
      )
    },
    {
      title: t('actions'),
      key: 'actions',
      render: (record: any) => (
        <Button 
          type="primary" 
          danger 
          onClick={() => handleDeleteUser(record.id)}
          disabled={record.id === currentUser?.id}
        >
          {t('delete')}
        </Button>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <h2>{t('userTitle')}</h2>
      <Card styles={{ body: { padding: 0 } }}>
        <Table columns={columns} dataSource={users} rowKey="id" loading={loading} />
      </Card>
    </div>
  );
};
