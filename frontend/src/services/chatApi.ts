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
    console.log('[Chat] 发送消息:', chatData);
    try {
      // 确保内容编码正确
      const encodedData = {
        ...chatData,
        content: chatData.content
      };
      
      const response = await apiRequest.post(
        API_ENDPOINTS.CHAT.SEND, 
        encodedData,
        {
          headers: {
            'Content-Type': 'application/json; charset=utf-8'
          }
        }
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
      
      console.log('[Chat] 安全检查完成，安全状态:', response.is_safe);
      return response;
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
      return response;
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
      return response;
    } catch (error: any) {
      console.error('[Chat] 情感支持失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '情感支持失败，请重试');
    }
  }

  /**
   * 智能聊天（通用聊天接口，会自动路由到合适的代理）
   */
static async intelligentChat(message: string, userId?: number, sessionId?: number): Promise<any> {
  console.log('[ChatAPI] 发送智能聊天消息:', { message, userId, sessionId });
  
  const chatData: ChatRequest = {
    content: message,
    user_id: userId,
    session_id: sessionId
  };

  console.log('[ChatAPI] 请求数据:', chatData);
  
  try {
    const response = await this.sendMessage(chatData);
    console.log('[ChatAPI] 收到响应:', response);
    return response;
  } catch (error) {
    console.error('[ChatAPI] 发送消息时出错:', error);
    throw error;
  }
}
}