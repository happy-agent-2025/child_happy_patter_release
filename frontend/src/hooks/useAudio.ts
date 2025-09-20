import { useState, useRef, useCallback } from 'react';
import { message } from 'antd';
import { AudioApiService } from '../services/audioApi';

export interface UseAudioReturn {
  isRecording: boolean;
  recordingTime: number;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  playTextAsAudio: (text: string) => Promise<void>;
}

export const useAudio = (): UseAudioReturn => {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordingTime, setRecordingTime] = useState<number>(0);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordingTimerRef = useRef<number | null>(null);

  // 获取支持的音频格式
  const getSupportedAudioFormat = useCallback(() => {
    const mimeTypes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/mpeg',
      'audio/wav',
      'audio/ogg;codecs=opus'
    ];
    
    const supportedTypes = mimeTypes.filter(type => 
      MediaRecorder.isTypeSupported(type)
    );
    
    console.log('浏览器支持的音频格式:', supportedTypes);
    
    const preferredTypes = [
      'audio/webm;codecs=opus',
      'audio/ogg;codecs=opus',
      'audio/webm',
      'audio/wav',
      'audio/mp4'
    ];
    
    for (const type of preferredTypes) {
      if (MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }
    
    return 'audio/webm;codecs=opus';
  }, []);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        }
      });
      
      const selectedType = getSupportedAudioFormat();
      console.log('选择的音频格式:', selectedType);
      
      const mediaRecorder = new MediaRecorder(stream, { 
        mimeType: selectedType,
        audioBitsPerSecond: 64000
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
        
        console.log('录音完成，时长:', recordingTime.toFixed(1) + 's', 
                   '大小:', (audioBlob.size / 1024).toFixed(1) + 'KB');
        
        if (recordingTime >= 1) {
          try {
            const fileName = `recording_${Date.now()}.${selectedType.includes('webm') ? 'webm' : 'wav'}`;
            const transcribeResponse = await AudioApiService.transcribeAudio({
              file: new File([audioBlob], fileName, { type: mediaRecorder.mimeType || 'audio/wav' }),
              preprocess: true
            });
            
            if (transcribeResponse.success && transcribeResponse.data && transcribeResponse.data.text && transcribeResponse.data.text.trim()) {
              return transcribeResponse.data.text;
            } else {
              message.warning('未识别到有效语音内容');
              return null;
            }
            
          } catch (error: any) {
            console.error('语音识别失败:', error);
            message.error('语音识别失败，请重试');
            return null;
          }
        } else {
          message.info('录音时间太短，已取消');
          return null;
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
  }, [recordingTime, getSupportedAudioFormat]);

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

  const playTextAsAudio = useCallback(async (text: string) => {
    try {
      const ttsResponse = await AudioApiService.synthesizeSpeech({
        text,
        voice_type: 'female',
        speed: 1.0,
        volume: 1.0
      });

      if (ttsResponse.success && ttsResponse.data && ttsResponse.data.audio_data) {
        await AudioApiService.playAudio(
          ttsResponse.data.audio_data, 
          ttsResponse.data.format || 'wav'
        );
        console.log('文本转语音播放成功');
      }
    } catch (error) {
      console.warn('文本转语音失败:', error);
      // 不阻止正常聊天流程
    }
  }, []);

  return {
    isRecording,
    recordingTime,
    startRecording,
    stopRecording,
    playTextAsAudio,
  };
};