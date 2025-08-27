import React from 'react';
import { List, Avatar, Typography, Space } from 'antd';
import { 
  UserOutlined, 
  SafetyOutlined, 
  BookOutlined, 
  HeartOutlined,
  RobotOutlined 
} from '@ant-design/icons';

const { Text } = Typography;

interface Message {
  id: number;
  content: string;
  sender: 'user' | 'meta' | 'safety' | 'edu' | 'emotion' | 'memory';
  timestamp: Date;
  isAudio?: boolean;
}

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const getAgentIcon = (sender: string) => {
    switch (sender) {
      case 'user':
        return <UserOutlined style={{ color: '#1890ff' }} />;
      case 'meta':
        return <RobotOutlined style={{ color: '#722ed1' }} />;
      case 'safety':
        return <SafetyOutlined style={{ color: '#fa541c' }} />;
      case 'edu':
        return <BookOutlined style={{ color: '#52c41a' }} />;
      case 'emotion':
        return <HeartOutlined style={{ color: '#eb2f96' }} />;
      case 'memory':
        return <RobotOutlined style={{ color: '#faad14' }} />;
      default:
        return <RobotOutlined />;
    }
  };

  const getAgentName = (sender: string) => {
    switch (sender) {
      case 'user':
        return '用户';
      case 'meta':
        return '元代理';
      case 'safety':
        return '安全代理';
      case 'edu':
        return '教育代理';
      case 'emotion':
        return '情感代理';
      case 'memory':
        return '记忆代理';
      default:
        return '未知代理';
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div style={{ height: '100%', overflowY: 'auto' }}>
      <List
        dataSource={messages}
        renderItem={(message) => (
          <List.Item
            style={{
              padding: '12px 16px',
              border: 'none',
              backgroundColor: message.sender === 'user' ? '#f0f8ff' : '#fff',
              marginBottom: '8px',
              borderRadius: '8px',
              borderLeft: `4px solid ${
                message.sender === 'user' ? '#1890ff' : 
                message.sender === 'meta' ? '#722ed1' :
                message.sender === 'safety' ? '#fa541c' :
                message.sender === 'edu' ? '#52c41a' :
                message.sender === 'emotion' ? '#eb2f96' : '#faad14'
              }`
            }}
          >
            <List.Item.Meta
              avatar={
                <Avatar 
                  size="small" 
                  icon={getAgentIcon(message.sender)}
                  style={{
                    backgroundColor: message.sender === 'user' ? '#1890ff' : 
                    message.sender === 'meta' ? '#722ed1' :
                    message.sender === 'safety' ? '#fa541c' :
                    message.sender === 'edu' ? '#52c41a' :
                    message.sender === 'emotion' ? '#eb2f96' : '#faad14'
                  }}
                />
              }
              title={
                <Space>
                  <Text strong>{getAgentName(message.sender)}</Text>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {formatTime(message.timestamp)}
                  </Text>
                </Space>
              }
              description={
                message.isAudio ? (
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '8px',
                    padding: '8px',
                    backgroundColor: '#f5f5f5',
                    borderRadius: '6px'
                  }}>
                    <span>🎵</span>
                    <Text>语音消息</Text>
                    <button 
                      style={{ 
                        padding: '4px 8px', 
                        fontSize: '12px',
                        backgroundColor: '#1890ff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      播放
                    </button>
                  </div>
                ) : (
                  <Text>{message.content}</Text>
                )
              }
            />
          </List.Item>
        )}
      />
    </div>
  );
};

export default MessageList;