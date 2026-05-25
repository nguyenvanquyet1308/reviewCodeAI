import React, { useEffect, useState } from 'react';
import { Card, Table, Typography, Button, Space, message } from 'antd';
import { GithubOutlined, LinkOutlined } from '@ant-design/icons';
import client from '../api/client';
import { RepositoryItem } from '../types/review';

const { Title, Text } = Typography;

export const RepositoryPage: React.FC = () => {
  const [repos, setRepos] = useState<RepositoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchRepositories = async () => {
    setLoading(true);
    try {
      const response = await client.get<RepositoryItem[]>('/repositories');
      setRepos(response.data);
    } catch (err) {
      console.error(err);
      message.error('Failed to load repositories.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRepositories();
  }, []);

  const columns = [
    {
      title: 'Repository Name',
      dataIndex: 'full_name',
      key: 'full_name',
      render: (name: string, record: RepositoryItem) => (
        <span style={{ fontWeight: 600 }}>
          <GithubOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          <a href={record.html_url} target="_blank" rel="noreferrer" style={{ color: '#e2e8f0' }}>
            {name}
          </a>
        </span>
      ),
    },
    {
      title: 'Starred / Link',
      key: 'link',
      width: 150,
      render: (_: unknown, record: RepositoryItem) => (
        <a href={record.html_url} target="_blank" rel="noreferrer">
          <Button size="small" icon={<LinkOutlined />}>
            GitHub URL
          </Button>
        </a>
      ),
    },
    {
      title: 'Total AI Reviews',
      dataIndex: 'review_count',
      key: 'review_count',
      width: 180,
      render: (count: number) => (
        <strong style={{ color: '#1890ff', fontSize: '15px' }}>{count}</strong>
      ),
    },
    {
      title: 'Last Reviewed At',
      dataIndex: 'last_reviewed_at',
      key: 'last_reviewed_at',
      width: 250,
      render: (dateStr: string | null) => (
        <Text style={{ color: '#8c8c8c' }}>
          {dateStr ? new Date(dateStr).toLocaleString() : 'Never reviewed'}
        </Text>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>
            Registered <span className="gradient-text">Repositories</span>
          </Title>
          <Text type="secondary">List of GitHub repositories active and tracked via incoming webhooks.</Text>
        </div>
        <Button type="primary" onClick={fetchRepositories} loading={loading}>
          Reload
        </Button>
      </div>

      <Table
        dataSource={repos}
        columns={columns}
        rowKey="id"
        loading={loading}
        className="glass-card"
        pagination={{ pageSize: 10 }}
        style={{ background: 'transparent' }}
      />
    </div>
  );
};
