import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Space, Input, Select, Button, Typography, message } from 'antd';// Correcting imports to 'antd' instead of 'react-redux'!
import { SearchOutlined, CheckCircleOutlined, CloseCircleOutlined, AlertOutlined, FileTextOutlined } from '@ant-design/icons';
import client from '../api/client';
import { ReviewJobItem } from '../types/review';
import { ReviewTable } from '../components/ReviewTable';

const { Title, Text } = Typography;
const { Option } = Select;

export const DashboardPage: React.FC = () => {
  const [jobs, setJobs] = useState<ReviewJobItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchRepo, setSearchRepo] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [filterRisk, setFilterRisk] = useState<string>('');

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (searchRepo) params.repository = searchRepo;
      if (filterStatus) params.status = filterStatus;
      if (filterRisk) params.risk_level = filterRisk;

      const response = await client.get<ReviewJobItem[]>('/reviews', { params });
      setJobs(response.data);
    } catch (err) {
      console.error(err);
      message.error('Failed to load review jobs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [filterStatus, filterRisk]);

  const handleSearch = () => {
    fetchJobs();
  };

  const handleReset = () => {
    setSearchRepo('');
    setFilterStatus('');
    setFilterRisk('');
    // We clear parameters, let's call API again.
    // Setting state is async, so we pass empty params directly
    setLoading(true);
    client.get<ReviewJobItem[]>('/reviews')
      .then(res => setJobs(res.data))
      .catch(() => message.error('Failed to reset filters.'))
      .finally(() => setLoading(false));
  };

  // Metrics computation from loaded dataset
  const totalReviews = jobs.length;
  const successReviews = jobs.filter(j => j.status === 'success').length;
  const failedReviews = jobs.filter(j => j.status === 'failed').length;
  const highRiskReviews = jobs.filter(j => j.risk_level === 'HIGH').length;

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>
            System <span className="gradient-text">Overview</span>
          </Title>
          <Text type="secondary">Real-time AI automated review statistics and tasks queue monitoring.</Text>
        </div>
        <Button type="primary" onClick={fetchJobs} loading={loading}>
          Reload
        </Button>
      </div>

      {/* Metrics Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card className="glass-card" style={{ borderLeft: '4px solid #1890ff' }}>
            <Statistic
              title={<span style={{ color: '#8c8c8c' }}>Total Reviews</span>}
              value={totalReviews}
              prefix={<FileTextOutlined style={{ color: '#1890ff', marginRight: 8 }} />}
              valueStyle={{ fontWeight: 700 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="glass-card" style={{ borderLeft: '4px solid #52c41a' }}>
            <Statistic
              title={<span style={{ color: '#8c8c8c' }}>Success</span>}
              value={successReviews}
              prefix={<CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />}
              valueStyle={{ fontWeight: 700 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="glass-card" style={{ borderLeft: '4px solid #ff4d4f' }}>
            <Statistic
              title={<span style={{ color: '#8c8c8c' }}>Failed</span>}
              value={failedReviews}
              prefix={<CloseCircleOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />}
              valueStyle={{ fontWeight: 700 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="glass-card" style={{ borderLeft: '4px solid #f5222d' }}>
            <Statistic
              title={<span style={{ color: '#8c8c8c' }}>High Risk PRs</span>}
              value={highRiskReviews}
              prefix={<AlertOutlined style={{ color: '#f5222d', marginRight: 8 }} />}
              valueStyle={{ fontWeight: 700 }}
            />
          </Card>
        </Col>
      </Row>

      {/* Filters Card */}
      <Card className="glass-card" style={{ marginBottom: 24 }}>
        <Space wrap size="middle" style={{ width: '100%' }}>
          <Input
            placeholder="Search repository..."
            prefix={<SearchOutlined />}
            value={searchRepo}
            onChange={(e) => setSearchRepo(e.target.value)}
            onPressEnter={handleSearch}
            style={{ width: 240 }}
          />
          <Select
            placeholder="Status"
            value={filterStatus}
            onChange={setFilterStatus}
            style={{ width: 140 }}
            allowClear
          >
            <Option value="">All Statuses</Option>
            <Option value="pending">Pending</Option>
            <Option value="running">Running</Option>
            <Option value="success">Success</Option>
            <Option value="failed">Failed</Option>
          </Select>
          <Select
            placeholder="Risk Level"
            value={filterRisk}
            onChange={setFilterRisk}
            style={{ width: 140 }}
            allowClear
          >
            <Option value="">All Risks</Option>
            <Option value="LOW">LOW</Option>
            <Option value="MEDIUM">MEDIUM</Option>
            <Option value="HIGH">HIGH</Option>
          </Select>
          <Button type="primary" onClick={handleSearch}>Filter</Button>
          <Button onClick={handleReset}>Reset</Button>
        </Space>
      </Card>

      {/* Table */}
      <ReviewTable jobs={jobs} loading={loading} />
    </div>
  );
};
