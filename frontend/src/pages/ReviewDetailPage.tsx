import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, Row, Col, Typography, Button, Space, Tabs, Table, Collapse, Alert, Empty, Skeleton, message } from 'antd';
import { GithubOutlined, ArrowLeftOutlined, LinkOutlined, AlertOutlined, BugOutlined, SafetyCertificateOutlined, SettingOutlined, EyeOutlined } from '@ant-design/icons';
import client from '../api/client';
import { ReviewDetail, ReviewIssue, SuggestedTestCase } from '../types/review';
import { ReviewStatusTag } from '../components/ReviewStatusTag';
import { RiskLevelTag } from '../components/RiskLevelTag';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

export const ReviewDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<ReviewDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const response = await client.get<ReviewDetail>(`/reviews/${id}`);
        setDetail(response.data);
      } catch (err) {
        console.error(err);
        message.error('Failed to load review details.');
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [id]);

  if (loading) {
    return <Skeleton active paragraph={{ rows: 12 }} />;
  }

  if (!detail) {
    return (
      <Card className="glass-card">
        <Empty description="Review not found" />
        <Link to="/">
          <Button type="primary">Back to Dashboard</Button>
        </Link>
      </Card>
    );
  }

  const issueColumns = [
    {
      title: 'File',
      dataIndex: 'file',
      key: 'file',
      render: (file: string) => <code style={{ color: '#58a6ff' }}>{file}</code>,
    },
    {
      title: 'Line',
      dataIndex: 'line',
      key: 'line',
      width: 85,
      render: (line: string) => <code style={{ color: '#ff7b72' }}>{line}</code>,
    },
    {
      title: 'Level',
      dataIndex: 'level',
      key: 'level',
      width: 100,
      render: (level: 'LOW' | 'MEDIUM' | 'HIGH') => <RiskLevelTag level={level} />,
    },
    {
      title: 'Issue Description',
      dataIndex: 'issue',
      key: 'issue',
      render: (text: string) => <Text style={{ color: '#e2e8f0' }}>{text}</Text>,
    },
    {
      title: 'AI Suggestion',
      dataIndex: 'suggestion',
      key: 'suggestion',
      render: (text: string) => <Text type="secondary">{text}</Text>,
    },
  ];

  const testColumns = [
    {
      title: 'Test Name',
      dataIndex: 'name',
      key: 'name',
      width: 250,
      render: (name: string) => <strong style={{ color: '#e2e8f0' }}>{name}</strong>,
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (prio: 'LOW' | 'MEDIUM' | 'HIGH') => <RiskLevelTag level={prio} />,
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (desc: string) => <Text type="secondary">{desc}</Text>,
    },
  ];

  const renderIssueTable = (issues: ReviewIssue[], typeName: string) => (
    <Table
      dataSource={issues}
      columns={issueColumns}
      rowKey={(record) => `${record.file}-${record.line}-${record.issue.slice(0, 10)}`}
      pagination={false}
      locale={{ emptyText: <Empty description={`No ${typeName} found in this Pull Request.`} /> }}
      style={{ background: 'transparent' }}
      size="middle"
    />
  );

  return (
    <div>
      {/* Back button and PR links */}
      <div style={{ marginBottom: 20 }}>
        <Link to="/">
          <Button icon={<ArrowLeftOutlined />} style={{ marginRight: 8 }}>
            Back to Dashboard
          </Button>
        </Link>
        {detail.github_comment_url && (
          <a href={detail.github_comment_url} target="_blank" rel="noreferrer">
            <Button type="primary" ghost icon={<GithubOutlined />} style={{ marginRight: 8 }}>
              View Review Comment
            </Button>
          </a>
        )}
        <a href={detail.pr_url} target="_blank" rel="noreferrer">
          <Button icon={<LinkOutlined />}>Open Pull Request</Button>
        </a>
      </div>

      {/* Title section */}
      <div style={{ marginBottom: 24 }}>
        <Space align="center" size="middle">
          <Title level={3} style={{ margin: 0, color: '#e2e8f0' }}>
            #{detail.pr_number} - {detail.pr_title}
          </Title>
          <ReviewStatusTag status={detail.status} />
          <RiskLevelTag level={detail.risk_level} />
        </Space>
        <div>
          <Text type="secondary">Author: <strong>{detail.pr_author}</strong> | Repository: <strong>{detail.repository_name}</strong></Text>
        </div>
      </div>

      {/* Recommendations & Summary */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} md={16}>
          <Card title="Summary" className="glass-card" style={{ height: '100%' }}>
            <Paragraph style={{ fontSize: '15px', lineHeight: '1.7', color: '#e2e8f0' }}>
              {detail.summary}
            </Paragraph>
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card title="Merge Recommendation" className="glass-card" style={{ height: '100%' }}>
            <div style={{ marginBottom: 16 }}>
              {detail.merge_recommendation.can_merge ? (
                <Alert
                  message="Approved"
                  description="AI recommends merging this Pull Request."
                  type="success"
                  showIcon
                />
              ) : (
                <Alert
                  message="Changes Requested"
                  description="AI recommends resolving critical issues before merging."
                  type="error"
                  showIcon
                />
              )}
            </div>
            <div>
              <Text strong style={{ color: '#8c8c8c' }}>Reasoning:</Text>
              <Paragraph style={{ marginTop: 8, color: '#e2e8f0' }}>
                {detail.merge_recommendation.reason}
              </Paragraph>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Tabs for findings */}
      <Card className="glass-card" style={{ marginBottom: 24 }}>
        <Tabs defaultActiveKey="bugs">
          <Tabs.TabPane
            tab={
              <span>
                <BugOutlined />
                Potential Bugs ({detail.potential_bugs.length})
              </span>
            }
            key="bugs"
          >
            {renderIssueTable(detail.potential_bugs, 'potential bugs')}
          </Tabs.TabPane>
          <Tabs.TabPane
            tab={
              <span>
                <SafetyCertificateOutlined />
                Security Issues ({detail.security_issues.length})
              </span>
            }
            key="security"
          >
            {renderIssueTable(detail.security_issues, 'security issues')}
          </Tabs.TabPane>
          <Tabs.TabPane
            tab={
              <span>
                <AlertOutlined />
                Code Smells ({detail.code_smells.length})
              </span>
            }
            key="smells"
          >
            {renderIssueTable(detail.code_smells, 'code smells')}
          </Tabs.TabPane>
          <Tabs.TabPane
            tab={
              <span>
                <SettingOutlined />
                Performance Issues ({detail.performance_issues.length})
              </span>
            }
            key="performance"
          >
            {renderIssueTable(detail.performance_issues, 'performance issues')}
          </Tabs.TabPane>
          <Tabs.TabPane
            tab={
              <span>
                <EyeOutlined />
                Suggested Test Cases ({detail.suggested_test_cases.length})
              </span>
            }
            key="testcases"
          >
            <Table
              dataSource={detail.suggested_test_cases}
              columns={testColumns}
              rowKey="name"
              pagination={false}
              locale={{ emptyText: <Empty description="No test cases suggested." /> }}
              style={{ background: 'transparent' }}
              size="middle"
            />
          </Tabs.TabPane>
        </Tabs>
      </Card>

      {/* Collapsible raw AI output */}
      <Collapse className="glass-card" ghost>
        <Panel header={<span style={{ color: '#8c8c8c' }}>Raw AI JSON Response</span>} key="1">
          <pre className="code-block">
            {detail.ai_raw_response}
          </pre>
        </Panel>
      </Collapse>
    </div>
  );
};
