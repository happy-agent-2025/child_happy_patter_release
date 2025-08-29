import { Avatar, Typography } from 'antd';
import { 
  UserOutlined,
  RobotOutlined 
} from '@ant-design/icons';

const { Text } = Typography;

interface Message {
  id: number;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  isAudio?: boolean;
  agentType?: 'meta' | 'safety' | 'edu' | 'emotion' | 'memory'; // 只在需要时显示代理类型
}

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const getSenderInfo = (message: Message) => {
    if (message.sender === 'user') {
      return {
        icon: <UserOutlined style={{ color: '#1890ff' }} />,
        name: '你',
        color: '#1890ff'
      };
    } else {
      return {
        icon: <RobotOutlined style={{ color: '#52c41a' }} />,
        name: 'Happy Partner',
        color: '#52c41a'
      };
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div style={{ height: '100%', overflowY: 'auto', padding: '10px' }}>
      {messages.map((message) => {
        const senderInfo = getSenderInfo(message);
        return (
          <div
            key={message.id}
            style={{
              display: 'flex',
              flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
              marginBottom: '12px',
              alignItems: 'flex-start'
            }}
          >
            <Avatar 
              size="small" 
              icon={senderInfo.icon}
              style={{
                backgroundColor: senderInfo.color,
                margin: message.sender === 'user' ? '0 0 0 8px' : '0 8px 0 0'
              }}
            />
            
            <div
              style={{
                maxWidth: '70%',
                backgroundColor: message.sender === 'user' ? '#1890ff' : '#f0f0f0',
                color: message.sender === 'user' ? 'white' : '#333',
                padding: '8px 12px',
                borderRadius: '12px',
                borderTopLeftRadius: message.sender === 'user' ? '12px' : '4px',
                borderTopRightRadius: message.sender === 'user' ? '4px' : '12px'
              }}
            >
              {message.isAudio ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span>🎵</span>
                  <Text style={{ color: message.sender === 'user' ? 'white' : '#333', fontSize: '12px' }}>
                    语音消息
                  </Text>
                </div>
              ) : (
                <Text style={{ color: message.sender === 'user' ? 'white' : '#333' }}>
                  {message.content}
                </Text>
              )}
              
              <div style={{ 
                textAlign: message.sender === 'user' ? 'right' : 'left',
                marginTop: '4px'
              }}>
                <Text 
                  type="secondary" 
                  style={{ 
                    fontSize: '10px', 
                    color: message.sender === 'user' ? 'rgba(255,255,255,0.7)' : '#999' 
                  }}
                >
                  {formatTime(message.timestamp)}
                </Text>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default MessageList;