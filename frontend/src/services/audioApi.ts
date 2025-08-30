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
      // 将base64音频数据转换为Blob
      const byteCharacters = atob(audioData);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: `audio/${format}` });
      
      // 创建音频URL并播放
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      
      audio.play().catch(error => {
        console.error('[Audio] 播放失败:', error);
      });
      
      // 清理URL
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
      };
      
    } catch (error: any) {
      console.error('[Audio] 音频播放失败:', error.message);
      throw new Error('音频播放失败');
    }
  }
}