import { apiRequest, API_ENDPOINTS } from './api';
import { 
  AudioTranscribeRequest,
  AudioTranscribeResponse,
  AudioSynthesizeRequest,
  AudioSynthesizeResponse
} from '../types/api';

// 扩展响应类型，确保包含success和data属性
export interface ExtendedApiResponse<T> {
  success: boolean;
  data?: T;
}

// 扩展音频转写响应类型
export interface ExtendedAudioTranscribeResponse extends AudioTranscribeResponse {
  text: string;
}

// 扩展音频合成响应类型
export interface ExtendedAudioSynthesizeResponse extends AudioSynthesizeResponse {
  audio_data: string;
  format: string; // 移除可选标记，使其与基础接口兼容
}

// 音频API服务类
export class AudioApiService {
  
  /**
   * 语音转文本
   */
  static async transcribeAudio(audioData: AudioTranscribeRequest): Promise<ExtendedApiResponse<ExtendedAudioTranscribeResponse>> {
    try {
      const formData = new FormData();
      formData.append('file', audioData.file);
      if (audioData.preprocess !== undefined) {
        formData.append('preprocess', audioData.preprocess.toString());
      }
      
      const response = await apiRequest.post(
        API_ENDPOINTS.AUDIO.TRANSCRIBE,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        }
      );
      
      console.log('[Audio] 语音转文本成功');
      
      // 包装响应为统一格式
      return {
        success: true,
        data: response.data as ExtendedAudioTranscribeResponse
      };
    } catch (error: any) {
      console.error('[Audio] 语音转文本失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '语音转文本失败');
    }
  }

  /**
   * 文本转语音
   */
  static async synthesizeSpeech(synthesizeData: AudioSynthesizeRequest): Promise<ExtendedApiResponse<ExtendedAudioSynthesizeResponse>> {
    try {
      const response = await apiRequest.post(
        API_ENDPOINTS.AUDIO.SYNTHESIZE,
        synthesizeData
      );
      
      console.log('[Audio] 文本转语音成功');
      
      // 包装响应为统一格式
      return {
        success: true,
        data: response.data as ExtendedAudioSynthesizeResponse
      };
    } catch (error: any) {
      console.error('[Audio] 文本转语音失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '文本转语音失败');
    }
  }

  /**
   * 播放音频数据
   */
  static async playAudio(audioData: string, format: string = 'wav'): Promise<void> {
    try {
      // 后端返回的是十六进制字符串，需要先转换
      console.log('[Audio] 原始音频数据长度:', audioData.length, '格式:', format);
      
      // 将十六进制字符串转换为字节数组
      const hex = audioData;
      const byteArray = new Uint8Array(hex.length / 2);
      for (let i = 0; i < hex.length; i += 2) {
        byteArray[i / 2] = parseInt(hex.substr(i, 2), 16);
      }
      
      const blob = new Blob([byteArray], { type: `audio/${format}` });
      console.log('[Audio] Blob大小:', blob.size, 'bytes');
      
      // 创建音频URL并播放
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      
      // 等待音频加载完成
      await new Promise((resolve, reject) => {
        audio.oncanplaythrough = resolve;
        audio.onerror = reject;
        
        // 设置超时
        setTimeout(() => reject(new Error('音频加载超时')), 5000);
      });
      
      // 播放音频
      await audio.play();
      console.log('[Audio] 音频播放成功');
      
      // 清理URL
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        console.log('[Audio] 音频播放完成，URL已清理');
      };
      
    } catch (error: any) {
      console.error('[Audio] 音频播放失败:', error.message, error);
      throw new Error(`音频播放失败: ${error.message}`);
    }
  }
}