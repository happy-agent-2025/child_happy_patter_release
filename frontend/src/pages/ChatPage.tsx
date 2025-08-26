import React from 'react';
import { Card } from 'antd';

const ChatPage: React.FC = () => {
  return (
    <div style={{ padding: '20px' }}>
      <Card title="聊天界面" style={{ height: '500px' }}>
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
            overflowY: 'auto'
          }}>
            {/* 消息列表将在这里显示 */}
            <div style={{ textAlign: 'center', color: '#999', padding: '20px' }}>
              消息列表区域
            </div>
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