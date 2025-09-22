import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Card, Typography, message, Button } from 'antd';
import { 
  AudioOutlined, 
  StopOutlined, 
  LoadingOutlined
} from '@ant-design/icons';
import MessageList from '../components/MessageList';
import SafetyFilter from '../components/SafetyFilter';
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

  // 添加自动滚动效果
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const [inputValue, setInputValue] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordingTime, setRecordingTime] = useState<number>(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordingTimerRef = useRef<number | null>(null);
  
  // 安全过滤状态
  const [safetyFilterEnabled, setSafetyFilterEnabled] = useState<boolean>(true);
  const [contentToFilter, setContentToFilter] = useState<string>('');
  const [showSafetyFilter, setShowSafetyFilter] = useState<boolean>(false);
  
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

      // 在组件内部或外部添加这个辅助函数
      const extractTranscriptionText = (response: any): { text: string; data: any } => {
        if (!response?.data) {
          return { text: '', data: null };
        }
        
        // 检查是否是嵌套结构 (response.data.data)
        if (response.data.data && typeof response.data.data === 'object') {
          return {
            text: response.data.data.text || '',
            data: response.data.data
          };
        }
        
        // 检查是否是直接结构 (response.data)
        if (typeof response.data === 'object') {
          return {
            text: response.data.text || '',
            data: response.data
          };
        }
        
        return { text: '', data: null };
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
            
            // 然后在语音识别处理部分使用
            const { text: recognizedText, data: transcriptionData } = extractTranscriptionText(transcribeResponse);
            console.log('识别文本:', recognizedText);
            console.log('完整数据:', transcriptionData);

            // 发送识别后的文本到聊天
            if (transcribeResponse.success && recognizedText) {
              await handleSendMessage(recognizedText);
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

  // 处理安全过滤完成
  const handleFilterComplete = (filteredContent: string, isSafe: boolean) => {
    setShowSafetyFilter(false);
    
    // 如果内容安全或已过滤，继续发送消息
    if (isSafe && filteredContent.trim()) {
      sendMessageToAPI(filteredContent);
    } else {
      setLoading(false);
      message.warning('消息内容不适宜，已被过滤');
    }
  };

  // 在组件内部添加这个辅助函数
  const extractChatResponse = (response: any): { content: string; agentType: string } => {
    let content = '抱歉，我无法理解您的问题。';
    let agentType = 'edu';
    
    try {
      // 处理不同层级的响应结构
      if (response?.data?.data?.response) {
        // 新的嵌套结构: response.data.data.response
        content = response.data.data.response;
        agentType = response.data.data.agent_type || 'edu';
      } else if (response?.data?.response) {
        // 直接数据结构: response.data.response
        content = response.data.response;
        agentType = response.data.agent_type || 'edu';
      } else if (response?.result?.filtered_content) {
        // 安全检查代理返回格式
        content = response.result.filtered_content;
        agentType = response.agent || response.agent_type || 'safety';
      } else if (response?.response) {
        // 教育代理返回格式
        content = response.response;
        agentType = response.agent || response.agent_type || 'edu';
      } else if (response?.answer) {
        // 其他代理可能的返回格式
        content = response.answer;
        agentType = response.agent || response.agent_type || 'meta';
      } else if (response?.message) {
        // 错误消息格式
        content = response.message;
        agentType = 'meta';
      } else if (typeof response === 'string') {
        // 如果响应本身就是字符串
        content = response;
      }
    } catch (error) {
      console.error('解析响应时出错:', error);
    }
    
    return { content, agentType };
  };
  
  // 发送消息到API
  const sendMessageToAPI = async (messageContent: string) => {
    try {
      console.log('发送消息:', messageContent);
      
      // 调用聊天API
      console.log('正在调用API...', `${import.meta.env.VITE_API_BASE_URL}/chat`);
      const response = await ChatApiService.intelligentChat(messageContent, 1);
      
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

      // 然后在 sendMessageToAPI 函数中使用
      const { content: aiContent, agentType } = extractChatResponse(response);
      console.log('响应内容:', aiContent);
      console.log('代理类型:', agentType);
      
      // 文本转语音播放
      try {
        const ttsResponse = await AudioApiService.synthesizeSpeech({
          text: aiContent,
          voice_type: 'female',
          speed: 1.0,
          volume: 1.0
        });
        
        if (ttsResponse.success && ttsResponse.data && ttsResponse.data.data.audio_data) {
          await AudioApiService.playAudio(ttsResponse.data.data.audio_data, ttsResponse.data.format || 'wav');
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
  };
  
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
      console.log('发送消息:', messageContent);
      setMessages(prev => [...prev, userMessage]);
      if (!content) {
        setInputValue('');
      }
      setLoading(true);
      
      // 检查是否启用安全过滤
      if (safetyFilterEnabled) {
        setContentToFilter(messageContent);
        setShowSafetyFilter(true);
      } else {
        // 不需要过滤，直接发送
        sendMessageToAPI(messageContent);
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
            {isRecording && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                marginLeft: 'auto',
                color: '#ff4d4f',
                fontSize: '12px'
              }}>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: '#ff4d4f',
                  marginRight: '4px',
                  animation: 'pulse 1s infinite'
                }} />
                录音中...
              </div>
            )}
          </div>
        } 
        style={{ 
          height: '600px',
          display: 'flex',
          flexDirection: 'column' // 添加flex布局
        }}
        bodyStyle={{ 
          padding: '16px',
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden' // 防止外部溢出
        }}
      >
        {/* 消息列表容器 - 修复滑动条 */}
        <div style={{ 
          flex: 1,
          border: '1px solid #d9d9d9',
          borderRadius: '6px',
          padding: '12px',
          marginBottom: '12px',
          backgroundColor: '#fafafa',
          overflowY: 'auto', // 启用垂直滚动
          overflowX: 'hidden', // 隐藏水平滚动
          minHeight: 0, // 关键：允许Flex项目收缩
          display: 'flex',
          flexDirection: 'column'
        }}>
          {/* 消息内容区域 */}
          <div style={{ 
            flex: 1,
            minHeight: 0, // 允许内容区域收缩
            position: 'relative'
          }}>
            <MessageList messages={messages} />
            <div ref={messagesEndRef} />
          </div>
          
          {/* 加载状态指示器 */}
          {loading && (
            <div style={{
              textAlign: 'center',
              padding: '12px',
              color: '#999',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'sticky',
              bottom: 0,
              backgroundColor: '#fafafa',
              borderTop: '1px solid #f0f0f0',
              marginTop: 'auto' // 推到容器底部
            }}>
              <LoadingOutlined style={{ marginRight: '8px' }} />
              思考中...
            </div>
          )}
        </div>

        {/* 安全过滤开关 */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '8px',
          padding: '8px 0',
          borderTop: '1px solid #f0f0f0'
        }}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            安全过滤: {safetyFilterEnabled ? '已启用' : '已关闭'}
          </Text>
          <Button 
            size="small" 
            type={safetyFilterEnabled ? 'primary' : 'default'}
            onClick={() => setSafetyFilterEnabled(!safetyFilterEnabled)}
          >
            {safetyFilterEnabled ? '关闭过滤' : '启用过滤'}
          </Button>
        </div>

        {/* 输入区域 */}
        <div style={{ 
          display: 'flex', 
          gap: '10px', 
          alignItems: 'center',
          flexShrink: 0 // 防止输入区域被压缩
        }}>
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
                fontSize: '14px',
                paddingRight: isRecording ? '80px' : '40px',
                backgroundColor: isRecording ? '#fffaf0' : '#fff',
                transition: 'all 0.2s'
              }}
              disabled={isRecording}
            />
            
            {/* 录音图标 */}
            <div 
              style={{
                position: 'absolute',
                left: '10px',
                top: '50%',
                transform: 'translateY(-50%)',
                cursor: 'pointer',
                padding: '4px',
                borderRadius: '50%',
                backgroundColor: isRecording ? '#fff1f0' : 'transparent',
                transition: 'background-color 0.2s'
              }}
              onMouseDown={handleMouseDown}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              onTouchStart={handleTouchStart}
              onTouchEnd={handleTouchEnd}
              onTouchCancel={handleTouchEnd}
              title="按住录音，松开发送"
            >
              {isRecording ? (
                <StopOutlined 
                  style={{ 
                    color: '#ff4d4f', 
                    fontSize: '16px'
                  }} 
                />
              ) : (
                <AudioOutlined style={{ color: '#1890ff', fontSize: '16px' }} />
              )}
            </div>
            
            {/* 录音时间显示 */}
            {isRecording && (
              <div style={{ 
                position: 'absolute',
                right: '10px',
                top: '50%',
                transform: 'translateY(-50%)',
                fontSize: '12px', 
                color: '#ff4d4f',
                fontWeight: 'bold'
              }}>
                {recordingTime.toFixed(1)}s
              </div>
            )}
          </div>
          
          <Button 
            type="primary"
            onClick={() => handleSendMessage()}
            disabled={(!inputValue.trim() && !isRecording) || loading}
            icon={loading ? <LoadingOutlined /> : undefined}
            style={{ 
              minWidth: '80px',
              backgroundColor: isRecording ? '#ff4d4f' : '#1890ff',
              borderColor: isRecording ? '#ff4d4f' : '#1890ff'
            }}
          >
            {isRecording ? '停止' : loading ? '发送中' : '发送'}
          </Button>
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
      
      {/* 安全过滤组件 */}
      {showSafetyFilter && (
        <SafetyFilter
          content={contentToFilter}
          onFilterComplete={handleFilterComplete}
          userId={1} // 默认用户ID
        />
      )}
    </div>
  );
};

export default ChatPage;