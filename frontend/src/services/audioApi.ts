import { apiRequest, API_ENDPOINTS } from './api';
import { 
  AudioTranscribeRequest,
  AudioTranscribeResponse,
  AudioSynthesizeRequest,
  AudioSynthesizeResponse
} from '../types/api';

// 音频API服务类
export class AudioApiService {
  
  /**
   * 语音转文本
   */
  static async transcribeAudio(audioData: AudioTranscribeRequest): Promise<AudioTranscribeResponse> {
    try {
      const formData = new FormData();
      formData.append('file', audioData.file);
      if (audioData.preprocess !== undefined) {
        formData.append('preprocess', audioData.preprocess.toString());
      }
      
      const response = await apiRequest.post<AudioTranscribeResponse>(
        API_ENDPOINTS.AUDIO.TRANSCRIBE,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        }
      );
      
      console.log('[Audio] 语音转文本成功');
      return response;
    } catch (error: any) {
      console.error('[Audio] 语音转文本失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '语音转文本失败');
    }
  }

  /**
   * 文本转语音
   */
  static async synthesizeSpeech(synthesizeData: AudioSynthesizeRequest): Promise<AudioSynthesizeResponse> {
    try {
      const response = await apiRequest.post<AudioSynthesizeResponse>(
        API_ENDPOINTS.AUDIO.SYNTHESIZE,
        synthesizeData
      );
      
      console.log('[Audio] 文本转语音成功');
      return response;
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