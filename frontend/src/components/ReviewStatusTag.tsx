import React from 'react';
import { Tag } from 'antd';
import { SyncOutlined, CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';

interface Props {
  status: 'pending' | 'running' | 'success' | 'failed';
}

export const ReviewStatusTag: React.FC<Props> = ({ status }) => {
  switch (status) {
    case 'pending':
      return <Tag icon={<ClockCircleOutlined />} color="default">Pending</Tag>;
    case 'running':
      return <Tag icon={<SyncOutlined spin />} color="processing">Running</Tag>;
    case 'success':
      return <Tag icon={<CheckCircleOutlined />} color="success">Success</Tag>;
    case 'failed':
      return <Tag icon={<CloseCircleOutlined />} color="error">Failed</Tag>;
    default:
      return <Tag>{status}</Tag>;
  }
};
