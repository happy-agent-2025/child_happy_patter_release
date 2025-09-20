import React from 'react';
import { Spin, Typography } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface LoadingSpinnerProps {
  text?: string;
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  text = '加载中...', 
  size = 'default',
  style 
}) => {
  const antIcon = <LoadingOutlined style={{ fontSize: size === 'large' ? 24 : 16 }} spin />;

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '12px',
      ...style
    }}>
      <Spin indicator={antIcon} size={size} />
      {text && (
        <Text style={{ 
          marginLeft: '8px', 
          color: '#999',
          fontSize: size === 'large' ? '16px' : '14px'
        }}>
          {text}
        </Text>
      )}
    </div>
  );
};

export default LoadingSpinner;