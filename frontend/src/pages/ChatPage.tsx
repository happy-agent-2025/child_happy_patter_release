import React, { useState } from 'react';
import { Card, Typography, message } from 'antd';
import MessageList from '../components/MessageList';
import { ChatApiService } from '../services/chatApi';

const { Text } = Typography;

interface Message {
  id: number;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  isAudio?: boolean;
  agentType?: 'meta' | 'safety' | 'edu' | 'emotion' | 'memory'; // 只在需要时显示代理类型
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      content: '你好！我是Happy Partner，很高兴为你服务！',
      sender: 'assistant',
      timestamp: new Date('2025-08-26T10:00:00'),
      agentType: 'meta',
    },
    {
      id: 2,
      content: '我想学习数学',
      sender: 'user',
      timestamp: new Date('2025-08-26T10:01:00'),
    },
    {
      id: 3,
      content: '欢迎学习数学！你想了解什么数学知识呢？比如加减法、乘法表还是几何图形？',
      sender: 'assistant',
      timestamp: new Date('2025-08-26T10:01:10'),
      agentType: 'edu',
    },
    {
      id: 4,
      content: '语音消息',
      sender: 'user',
      timestamp: new Date('2025-08-26T10:02:00'),
      isAudio: true,
    },
    {
      id: 5,
      content: '我听到了你的语音消息！让我为你解释乘法表的知识。',
      sender: 'assistant',
      timestamp: new Date('2025-08-26T10:02:30'),
      agentType: 'edu',
    },
  ]);
  
  const [inputValue, setInputValue] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  
  // 处理消息发送
  const handleSendMessage = async () => {
    if (inputValue.trim() && !loading) {
      const userMessage: Message = {
        id: messages.length + 1,
        content: inputValue,
        sender: 'user',
        timestamp: new Date(),
      };
      
      // 立即添加用户消息到界面
      const userMessages = [...messages, userMessage];
      setMessages(userMessages);
      const currentInput = inputValue;
      setInputValue('');
      setLoading(true);

      try {
        console.log('发送消息:', currentInput);
        
        // 调用聊天API
        console.log('正在调用API...', `${import.meta.env.VITE_API_BASE_URL}/chat`);
        const response = await ChatApiService.intelligentChat(currentInput, 1);
        
        // 添加AI回复消息
        console.log('API响应:', response);
        console.log('响应字段检查:', {
          hasResponse: !!response.response,
          hasAnswer: !!response.answer,
          hasMessage: !!response.message,
          hasResult: !!response.result,
          hasAgent: !!response.agent,
          responseKeys: Object.keys(response)
        });
        
        // 根据后端实际返回格式解析内容
        let content = '抱歉，我无法理解您的问题。';
        if (response.result && response.result.filtered_content) {
          // 安全检查代理返回格式
          content = response.result.filtered_content;
        } else if (response.response) {
          // 教育代理返回格式
          content = response.response;
        } else if (response.answer) {
          // 其他代理可能的返回格式
          content = response.answer;
        } else if (response.message) {
          // 错误消息格式
          content = response.message;
        } else if (typeof response === 'string') {
          // 如果响应本身就是字符串
          content = response;
        } else {
          // 尝试将响应转换为字符串
          content = JSON.stringify(response, null, 2);
        }
        
        const aiMessage: Message = {
          id: Date.now(), // 使用时间戳作为唯一ID
          content: content,
          sender: 'assistant',
          timestamp: new Date(),
          agentType: response.agent || response.agent_type || 'edu', // 从响应中获取代理类型
        };
        
        // 使用函数式更新确保获取最新的消息状态
        setMessages(prevMessages => [...prevMessages, aiMessage]);
        
      } catch (error: any) {
        console.error('发送消息失败 - 详细错误:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status,
          stack: error.stack
        });
        
        // 显示更详细的错误信息
        const errorMessageContent = error.response?.data?.detail || error.message || '发送消息失败，请重试';
        message.error(`发送失败: ${errorMessageContent}`);
        
        // 发送失败时添加错误消息
        const errorMessage: Message = {
          id: Date.now(),
          content: `错误: ${errorMessageContent}`,
          sender: 'assistant',
          timestamp: new Date(),
          agentType: 'meta',
        };
        
        // 使用函数式更新确保获取最新的消息状态
        setMessages(prevMessages => [...prevMessages, errorMessage]);
      } finally {
        setLoading(false);
      }
    }
  };
  
  // 处理键盘事件
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };
  
  // 根据最新消息确定当前代理
  const getCurrentAgent = () => {
    const lastAssistantMessage = messages.filter(m => m.sender === 'assistant').slice(-1)[0];
    if (!lastAssistantMessage?.agentType) return '智能助手';
    
    const agentTypeMap = {
      'meta': '智能路由代理',
      'safety': '安全检查代理',
      'edu': '教育辅导代理',
      'emotion': '情感支持代理',
      'memory': '记忆管理代理'
    };
    
    return agentTypeMap[lastAssistantMessage.agentType] || '智能助手';
  };

  return (
    <div style={{ padding: '20px' }}>
      <Card 
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>儿童教育AI聊天</span>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              当前服务: {getCurrentAgent()}
            </Text>
          </div>
        } 
        style={{ height: '600px' }}
      >
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
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
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
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || loading}
              style={{ 
                padding: '8px 16px', 
                backgroundColor: (inputValue.trim() && !loading) ? '#1890ff' : '#d9d9d9', 
                color: 'white', 
                border: 'none', 
                borderRadius: '6px',
                cursor: (inputValue.trim() && !loading) ? 'pointer' : 'not-allowed',
                fontSize: '14px'
              }}
            >
              {loading ? '发送中...' : '发送'}
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ChatPage;