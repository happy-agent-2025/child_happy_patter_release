import React, { useState } from 'react';
import { Button } from 'antd';
import { AudioOutlined, StopOutlined, LoadingOutlined } from '@ant-design/icons';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  onStartRecording: () => void;
  onStopRecording: () => void;
  loading: boolean;
  isRecording: boolean;
  recordingTime: number;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onStartRecording,
  onStopRecording,
  loading,
  isRecording,
  recordingTime,
  disabled = false
}) => {
  const [inputValue, setInputValue] = useState<string>('');

  const handleSendMessage = () => {
    if (inputValue.trim() && !loading) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleMouseDown = () => {
    if (!isRecording && !disabled) {
      onStartRecording();
    }
  };

  const handleMouseUp = () => {
    if (isRecording) {
      onStopRecording();
    }
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault();
    if (!isRecording && !disabled) {
      onStartRecording();
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault();
    if (isRecording) {
      onStopRecording();
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      gap: '10px', 
      alignItems: 'center',
      flexShrink: 0
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
          disabled={isRecording || disabled}
        />
        
        {/* 录音图标 */}
        <div 
          style={{
            position: 'absolute',
            left: '10px',
            top: '50%',
            transform: 'translateY(-50%)',
            cursor: disabled ? 'not-allowed' : 'pointer',
            padding: '4px',
            borderRadius: '50%',
            backgroundColor: isRecording ? '#fff1f0' : 'transparent',
            transition: 'background-color 0.2s',
            opacity: disabled ? 0.5 : 1
          }}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
          onTouchCancel={handleTouchEnd}
          title={disabled ? '功能暂时不可用' : '按住录音，松开发送'}
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
        onClick={handleSendMessage}
        disabled={(!inputValue.trim() && !isRecording) || loading || disabled}
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
  );
};

export default ChatInput;