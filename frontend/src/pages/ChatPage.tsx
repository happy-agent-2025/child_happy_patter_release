import React, { useState, useRef, useCallback } from 'react';
import { Card, Typography, message, Button } from 'antd';
import { 
  AudioOutlined, 
  StopOutlined, 
  LoadingOutlined 
} from '@ant-design/icons';
import MessageList from '../components/MessageList';
import { ChatApiService } from '../services/chatApi';
import { AudioApiService } from '../services/audioApi';

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
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordingTime, setRecordingTime] = useState<number>(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordingTimerRef = useRef<number | null>(null);
  
  // 开始录音
  const startRecording = useCallback(async () => {
    try {
      // 检查浏览器支持的音频格式
      const mimeTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/mp4',
        'audio/mpeg',
        'audio/wav',
        'audio/ogg;codecs=opus'
      ];
      
      const supportedTypes = mimeTypes.filter(type => {
        return MediaRecorder.isTypeSupported(type);
      });
      
      console.log('浏览器支持的音频格式:', supportedTypes);
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        }
      });
      
      // 选择最佳音频格式（优先选择opus编码的格式）
      const preferredTypes = [
        'audio/webm;codecs=opus',    // Chrome/Firefox
        'audio/ogg;codecs=opus',     // Firefox
        'audio/webm',                // 通用webm
        'audio/wav',                 // WAV格式
        'audio/mp4'                  // MP4格式
      ];
      
      let selectedType = 'audio/webm;codecs=opus';
      for (const type of preferredTypes) {
        if (MediaRecorder.isTypeSupported(type)) {
          selectedType = type;
          break;
        }
      }
      
      console.log('选择的音频格式:', selectedType, '比特率: 64kbps');
      
      const mediaRecorder = new MediaRecorder(stream, { 
        mimeType: selectedType,
        audioBitsPerSecond: 64000 // 64kbps音质，适合语音识别
      });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: mediaRecorder.mimeType || 'audio/webm' 
        });
        
        console.log('录音完成，时长:', recordingTime.toFixed(1) + 's', '大小:', (audioBlob.size / 1024).toFixed(1) + 'KB', '格式:', mediaRecorder?.mimeType || 'unknown', '比特率:', Math.round(audioBlob.size * 8 / recordingTime / 1000) + 'kbps');
        
        // 检查录音时长是否超过1秒
        if (recordingTime >= 1) {
          try {
            setLoading(true);
            
            // 语音转文本
            const fileName = `recording_${Date.now()}.${selectedType.includes('webm') ? 'webm' : 'wav'}`;
            const transcribeResponse = await AudioApiService.transcribeAudio({
              file: new File([audioBlob], fileName, { type: mediaRecorder.mimeType || 'audio/wav' }),
              preprocess: true
            });
            
            // 发送识别后的文本到聊天
            if (transcribeResponse.text && transcribeResponse.text.trim()) {
              await handleSendMessage(transcribeResponse.text);
            } else {
              message.warning('未识别到有效语音内容');
            }
            
          } catch (error: any) {
            console.error('语音识别失败:', error);
            message.error('语音识别失败，请重试');
          } finally {
            setLoading(false);
          }
        } else {
          message.info('录音时间太短，已取消');
        }
        
        // 停止所有音频轨道
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // 开始计时
      recordingTimerRef.current = window.setInterval(() => {
        setRecordingTime(prev => prev + 0.1);
      }, 100);
      
    } catch (error) {
      console.error('无法访问麦克风:', error);
      message.error('无法访问麦克风，请检查权限设置');
    }
  }, [recordingTime]);

  // 停止录音
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (recordingTimerRef.current) {
        window.clearInterval(recordingTimerRef.current);
        recordingTimerRef.current = null;
      }
    }
  }, [isRecording]);

  // 处理消息发送
  const handleSendMessage = async (content?: string) => {
    const messageContent = content || inputValue;
    
    if (messageContent.trim() && !loading) {
      const userMessage: Message = {
        id: Date.now(),
        content: messageContent,
        sender: 'user',
        timestamp: new Date(),
      };
      
      // 立即添加用户消息到界面
      setMessages(prev => [...prev, userMessage]);
      if (!content) {
        setInputValue('');
      }
      setLoading(true);
      
      const currentInput = messageContent;
      
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
        let aiContent = '抱歉，我无法理解您的问题。';
        if (response.result && response.result.filtered_content) {
          // 安全检查代理返回格式
          aiContent = response.result.filtered_content;
        } else if (response.response) {
          // 教育代理返回格式
          aiContent = response.response;
        } else if (response.answer) {
          // 其他代理可能的返回格式
          aiContent = response.answer;
        } else if (response.message) {
          // 错误消息格式
          aiContent = response.message;
        } else if (typeof response === 'string') {
          // 如果响应本身就是字符串
          aiContent = response;
        } else {
          // 尝试将响应转换为字符串
          aiContent = JSON.stringify(response, null, 2);
        }
        
        // 文本转语音播放
        try {
          const ttsResponse = await AudioApiService.synthesizeSpeech({
            text: aiContent,
            voice_type: 'female',
            speed: 1.0,
            volume: 1.0
          });

          console.log('文本转语音成功，播放中...', ttsResponse);
          
          if (ttsResponse.audio_data) {
            await AudioApiService.playAudio(ttsResponse.audio_data, ttsResponse.format);
          }
        } catch (ttsError) {
          console.warn('文本转语音失败:', ttsError);
          // 不阻止正常聊天流程，只是无法播放语音
        }
        
        const aiMessage: Message = {
          id: Date.now(), // 使用时间戳作为唯一ID
          content: aiContent,
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
        message.error('发送消息失败，请重试');
        
        // 发送失败时添加错误消息
        const errorMessage: Message = {
          id: Date.now(),
          content: '抱歉，消息发送失败，请稍后重试。',
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

  // 处理鼠标按下事件（开始录音）
  const handleMouseDown = () => {
    if (!isRecording) {
      startRecording();
    }
  };

  // 处理鼠标松开事件（停止录音）
  const handleMouseUp = () => {
    if (isRecording) {
      stopRecording();
    }
  };

  // 处理触摸事件（移动端支持）
  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault();
    if (!isRecording) {
      startRecording();
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault();
    if (isRecording) {
      stopRecording();
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
          
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <input 
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="输入消息或长按麦克风录音..." 
                style={{ 
                  width: '100%',
                  padding: '8px 12px 8px 40px', 
                  border: '1px solid #d9d9d9', 
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              />
              <div 
                style={{
                  position: 'absolute',
                  left: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  cursor: 'pointer'
                }}
                onMouseDown={handleMouseDown}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                onTouchStart={handleTouchStart}
                onTouchEnd={handleTouchEnd}
                onTouchCancel={handleTouchEnd}
              >
                {isRecording ? (
                  <StopOutlined 
                    style={{ 
                      color: '#ff4d4f', 
                      fontSize: '16px',
                      animation: 'pulse 1s infinite'
                    }} 
                  />
                ) : (
                  <AudioOutlined style={{ color: '#1890ff', fontSize: '16px' }} />
                )}
              </div>
            </div>
            
            {isRecording && (
              <div style={{ 
                fontSize: '12px', 
                color: '#ff4d4f',
                minWidth: '40px',
                textAlign: 'center'
              }}>
                {recordingTime.toFixed(1)}s
              </div>
            )}
            
            <Button 
              type="primary"
              onClick={() => handleSendMessage()}
              disabled={(!inputValue.trim() && !isRecording) || loading}
              icon={loading ? <LoadingOutlined /> : undefined}
              style={{ 
                minWidth: '80px',
                backgroundColor: isRecording ? '#ff4d4f' : '#1890ff'
              }}
            >
              {isRecording ? '停止' : loading ? '发送中' : '发送'}
            </Button>
          </div>
        </div>
        
        {/* 录音动画样式 */}
        <style>
          {`
            @keyframes pulse {
              0% { opacity: 1; }
              50% { opacity: 0.5; }
              100% { opacity: 1; }
            }
          `}
        </style>
      </Card>
    </div>
  );
};

export default ChatPage;