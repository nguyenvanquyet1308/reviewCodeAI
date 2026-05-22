import React from 'react';
import { Tag } from 'antd';
import { WarningOutlined, AlertOutlined, InfoCircleOutlined } from '@ant-design/icons';

interface Props {
  level: 'LOW' | 'MEDIUM' | 'HIGH' | null;
}

export const RiskLevelTag: React.FC<Props> = ({ level }) => {
  if (!level) return <Tag color="default">N/A</Tag>;
  
  switch (level.toUpperCase()) {
    case 'LOW':
      return <Tag icon={<InfoCircleOutlined />} color="success">LOW</Tag>;
    case 'MEDIUM':
      return <Tag icon={<WarningOutlined />} color="warning">MEDIUM</Tag>;
    case 'HIGH':
      return <Tag icon={<AlertOutlined />} color="error">HIGH</Tag>;
    default:
      return <Tag>{level}</Tag>;
  }
};
