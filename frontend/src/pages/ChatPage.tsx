import React, { useState } from 'react';
import { Card } from 'antd';
import MessageList from '../components/MessageList';

interface Message {
  id: number;
  content: string;
  sender: 'user' | 'meta' | 'safety' | 'edu' | 'emotion' | 'memory';
  timestamp: Date;
  isAudio?: boolean;
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      content: '你好！我是Happy Partner，很高兴为你服务！',
      sender: 'meta',
      timestamp: new Date('2025-08-26T10:00:00'),
    },
    {
      id: 2,
      content: '我想学习数学',
      sender: 'user',
      timestamp: new Date('2025-08-26T10:01:00'),
    },
    {
      id: 3,
      content: '好的！让我为你连接到教育代理来帮助学习数学。',
      sender: 'meta',
      timestamp: new Date('2025-08-26T10:01:10'),
    },
    {
      id: 4,
      content: '欢迎学习数学！你想了解什么数学知识呢？比如加减法、乘法表还是几何图形？',
      sender: 'edu',
      timestamp: new Date('2025-08-26T10:01:20'),
    },
    {
      id: 5,
      content: '语音消息',
      sender: 'user',
      timestamp: new Date('2025-08-26T10:02:00'),
      isAudio: true,
    },
    {
      id: 6,
      content: '我听到了你的语音消息！让我为你解释乘法表的知识。',
      sender: 'edu',
      timestamp: new Date('2025-08-26T10:02:30'),
    },
  ]);

  return (
    <div style={{ padding: '20px' }}>
      <Card title="儿童教育AI聊天" style={{ height: '600px' }}>
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          height: '100%',
          justifyContent: 'space-between'
        }}>
          <div style={{ 
            flex: 1, 
            border: '1px solid #d9d9d9', 
            borderRadius: '6px', 
            padding: '10px',
            marginBottom: '10px',
            overflowY: 'auto',
            backgroundColor: '#fafafa'
          }}>
            <MessageList messages={messages} />
          </div>
          
          <div style={{ display: 'flex', gap: '10px' }}>
            <input 
              placeholder="输入消息..." 
              style={{ 
                flex: 1, 
                padding: '8px 12px', 
                border: '1px solid #d9d9d9', 
                borderRadius: '6px',
                fontSize: '14px'
              }}
            />
            <button 
              style={{ 
                padding: '8px 16px', 
                backgroundColor: '#1890ff', 
                color: 'white', 
                border: 'none', 
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              发送
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ChatPage;