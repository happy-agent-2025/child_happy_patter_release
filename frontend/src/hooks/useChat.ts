import { useState, useCallback } from 'react';
import { message } from 'antd';
import { ChatApiService } from '../services/chatApi';
import { StoryApiService } from '../services/storyApi';

export interface Message {
  id: number;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  isAudio?: boolean;
  agentType?: 'meta' | 'safety' | 'edu' | 'emotion' | 'memory' | 'story';
}

export interface UseChatReturn {
  messages: Message[];
  loading: boolean;
  sendMessage: (content: string) => Promise<void>;
  addMessage: (message: Message) => void;
  clearMessages: () => void;
}

export const useChat = (): UseChatReturn => {
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

  const [loading, setLoading] = useState<boolean>(false);

  const addMessage = useCallback((newMessage: Message) => {
    setMessages(prev => [...prev, newMessage]);
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || loading) return;

    // 添加用户消息
    const userMessage: Message = {
      id: Date.now(),
      content,
      sender: 'user',
      timestamp: new Date(),
    };
    
    addMessage(userMessage);
    setLoading(true);

    try {
      console.log('发送消息:', content);
      
      const response = await StoryApiService.intelligentStory(content, '1');
      
      // 统一响应格式处理
      let aiContent = '抱歉，我无法理解您的问题。';
      let agentType: Message['agentType'] = 'meta';
      
      if (response.success && response.data) {
        const data = response.data;
        aiContent = data.response || data.content || data.answer || data.message || aiContent;
        agentType = 'story';
      } else if (response.response) {
        aiContent = response.response;
        agentType = 'story';
      }
      
      const aiMessage: Message = {
        id: Date.now() + 1,
        content: aiContent,
        sender: 'assistant',
        timestamp: new Date(),
        agentType,
      };
      
      addMessage(aiMessage);
      
    } catch (error: any) {
      console.error('发送消息失败:', error);
      message.error('发送消息失败，请重试');
      
      const errorMessage: Message = {
        id: Date.now() + 1,
        content: '抱歉，消息发送失败，请稍后重试。',
        sender: 'assistant',
        timestamp: new Date(),
        agentType: 'meta',
      };
      
      addMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [loading, addMessage]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    loading,
    sendMessage,
    addMessage,
    clearMessages,
  };
};