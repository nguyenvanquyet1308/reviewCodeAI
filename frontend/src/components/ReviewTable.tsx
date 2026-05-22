import React from 'react';
import { Table, Button } from 'antd';
import { EyeOutlined, GithubOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { ReviewJobItem } from '../types/review';
import { ReviewStatusTag } from './ReviewStatusTag';
import { RiskLevelTag } from './RiskLevelTag';

interface Props {
  jobs: ReviewJobItem[];
  loading: boolean;
}

export const ReviewTable: React.FC<Props> = ({ jobs, loading }) => {
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Repository',
      dataIndex: 'repository_name',
      key: 'repository_name',
      render: (name: string) => (
        <span style={{ fontWeight: 500 }}>
          <GithubOutlined style={{ marginRight: 8 }} />
          {name}
        </span>
      ),
    },
    {
      title: 'Pull Request',
      key: 'pr',
      render: (_: unknown, record: ReviewJobItem) => (
        <div>
          <span style={{ fontWeight: 600, color: '#1890ff' }}>#{record.pr_number}</span>{' '}
          <span style={{ color: '#e2e8f0' }}>{record.pr_title}</span>
        </div>
      ),
    },
    {
      title: 'Author',
      dataIndex: 'author',
      key: 'author',
      width: 120,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: 'pending' | 'running' | 'success' | 'failed') => (
        <ReviewStatusTag status={status} />
      ),
    },
    {
      title: 'Risk Level',
      dataIndex: 'risk_level',
      key: 'risk_level',
      width: 120,
      render: (level: 'LOW' | 'MEDIUM' | 'HIGH' | null) => (
        <RiskLevelTag level={level} />
      ),
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (dateStr: string) => new Date(dateStr).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 120,
      render: (_: unknown, record: ReviewJobItem) => (
        <Link to={`/reviews/${record.id}`}>
          <Button type="primary" ghost icon={<EyeOutlined />}>
            Detail
          </Button>
        </Link>
      ),
    },
  ];

  return (
    <Table
      dataSource={jobs}
      columns={columns}
      rowKey="id"
      loading={loading}
      className="glass-card"
      pagination={{ pageSize: 8 }}
      style={{ background: 'transparent' }}
    />
  );
};
