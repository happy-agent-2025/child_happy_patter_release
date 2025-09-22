import { apiRequest, API_ENDPOINTS } from './api';
import { 
  ChatRequest,
  SafetyCheckRequest,
  SafetyCheckResponse,
  EduQuestionRequest,
  EduQuestionResponse,
  EmotionSupportRequest,
  EmotionSupportResponse
} from '../types/api';

// 聊天API服务类
export class ChatApiService {
  
  /**
   * 发送聊天消息
   */
  static async sendMessage(chatData: ChatRequest): Promise<any> {
    try {
      const response = await apiRequest.post(
        API_ENDPOINTS.CHAT.SEND, 
        chatData
      );
      
      console.log('[Chat] 消息发送成功');
      return response;
    } catch (error: any) {
      console.error('[Chat] 消息发送失败 - 详细错误:', {
        message: error.message,
        code: error.code,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          data: error.config?.data
        }
      });
      throw new Error(error.response?.data?.detail || '消息发送失败，请重试');
    }
  }

  /**
   * 安全检查
   */
  static async checkSafety(safetyData: SafetyCheckRequest): Promise<SafetyCheckResponse> {
    try {
      const response = await apiRequest.post<SafetyCheckResponse>(
        API_ENDPOINTS.CHAT.SAFETY_CHECK, 
        safetyData
      );
      
      console.log('[Chat] 安全检查完成，安全状态:', response.data.is_safe);
      return response.data;
    } catch (error: any) {
      console.error('[Chat] 安全检查失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '安全检查失败');
    }
  }

  /**
   * 教育问答
   */
  static async askEducationQuestion(eduData: EduQuestionRequest): Promise<EduQuestionResponse> {
    try {
      const response = await apiRequest.post<EduQuestionResponse>(
        API_ENDPOINTS.CHAT.EDU_ASK, 
        eduData
      );
      
      console.log('[Chat] 教育问答响应成功');
      return response.data;
    } catch (error: any) {
      console.error('[Chat] 教育问答失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '教育问答失败，请重试');
    }
  }

  /**
   * 情感支持
   */
  static async getEmotionSupport(emotionData: EmotionSupportRequest): Promise<EmotionSupportResponse> {
    try {
      const response = await apiRequest.post<EmotionSupportResponse>(
        API_ENDPOINTS.CHAT.EMOTION_SUPPORT, 
        emotionData
      );
      
      console.log('[Chat] 情感支持响应成功');
      return response.data;
    } catch (error: any) {
      console.error('[Chat] 情感支持失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '情感支持失败，请重试');
    }
  }

  /**
   * 智能聊天（通用聊天接口，会自动路由到合适的代理）
   */
  static async intelligentChat(message: string, userId?: number, sessionId?: number): Promise<any> {
    const chatData: ChatRequest = {
      content: message,
      user_id: userId,
      session_id: sessionId
    };

    return this.sendMessage(chatData);
  }
}