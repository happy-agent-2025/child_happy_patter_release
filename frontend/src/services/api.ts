import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// 统一的API响应格式
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  code?: number;
}

// API端点配置
export const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    ME: '/auth/me',
  },
  
  // 聊天相关
  CHAT: {
    SEND: '/story/create',
    SAFETY_CHECK: '/safety/check',
    EDU_ASK: '/edu/ask',
    EMOTION_SUPPORT: '/emotion/support',
  },
  
  // 音频相关
  AUDIO: {
    TRANSCRIBE: '/audio/transcribe',
    SYNTHESIZE: '/audio/synthesize',
    PROCESS: '/audio/process',
  },
  
  // 声纹相关
  VOICE: {
    REGISTER: '/voice/register',
    VERIFY: '/voice/verify',
  },
  
  // 记忆管理
  MEMORY: {
    MANAGE: '/memory/manage',
  },
  
  // 用户相关
  USERS: {
    CONVERSATIONS: (userId: number) => `/users/${userId}/conversations`,
    RECENT_CONVERSATIONS: (userId: number) => `/users/${userId}/conversations/recent`,
    CONVERSATION_BY_AGENT: (userId: number, agentType: string) => `/users/${userId}/conversations/${agentType}`,
    SECURITY_LOGS: (userId: number) => `/users/${userId}/security-logs`,
    ACTIVITY_STATS: (userId: number) => `/users/${userId}/activity-stats`,
    LEARNING_PROGRESS: (userId: number) => `/users/${userId}/learning-progress`,
    CONTENT_FILTERS: (userId: number) => `/users/${userId}/content-filters`,
    USAGE_LIMITS: (userId: number) => `/users/${userId}/usage-limits`,
    SESSIONS: (userId: number) => `/users/${userId}/sessions`,
  },
  
  // 会话相关
  SESSIONS: {
    INFO: (sessionId: number) => `/sessions/${sessionId}`,
    DELETE: (sessionId: number) => `/sessions/${sessionId}`,
    CONVERSATIONS: (sessionId: number) => `/sessions/${sessionId}/conversations`,
    UPDATE_TITLE: (sessionId: number) => `/sessions/${sessionId}/title`,
    ACTIVATE: (sessionId: number) => `/sessions/${sessionId}/activate`,
    DEACTIVATE: (sessionId: number) => `/sessions/${sessionId}/deactivate`,
  },

  // LangGraph相关
  LANGGRAPH: {
    CHAT: '/langgraph/chat',
    CHAT_STREAM: '/langgraph/chat/stream',
    WORKFLOW_STATE: '/langgraph/workflow/state',
    CONVERSATION_FLOW: '/langgraph/analytics/conversation-flow',
    CREATE_SESSION: '/langgraph/session/create',
    SESSION_HISTORY: (sessionId: number) => `/langgraph/session/${sessionId}/history`,
    USER_INSIGHTS: (userId: number) => `/langgraph/users/${userId}/insights`,
    TEST_WORKFLOW: '/langgraph/test/workflow',
  },
};

// 创建axios实例
const createApiInstance = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // 请求拦截器
  instance.interceptors.request.use(
    (config) => {
      // 添加认证token
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      // 添加请求ID用于追踪
      config.headers['X-Request-ID'] = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        headers: config.headers,
        data: config.data
      });

      return config;
    },
    (error) => {
      console.error('[API Request Error]', error);
      return Promise.reject(error);
    }
  );

  // 响应拦截器
  instance.interceptors.response.use(
    (response: AxiosResponse): AxiosResponse<ApiResponse> => {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data
      });

      // 统一响应格式处理
      const originalData = response.data;
      
      // 如果后端已经返回标准格式，直接使用
      if (originalData && typeof originalData === 'object' && 'success' in originalData) {
        return response;
      }

      // 否则包装成标准格式
      const wrappedData: ApiResponse = {
        success: true,
        data: originalData,
        message: 'Success'
      };

      response.data = wrappedData;
      return response;
    },
    (error: AxiosError) => {
      console.error('[API Response Error]', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: {
          method: error.config?.method,
          url: error.config?.url,
          baseURL: error.config?.baseURL
        }
      });

      // 统一错误格式处理
      const errorResponse: ApiResponse = {
        success: false,
        error: error.message,
        message: getErrorMessage(error),
        code: error.response?.status || 0
      };

      // 特殊错误处理
      if (error.response?.status === 401) {
        // 未授权，清除token并跳转登录
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
      }

      // 将错误包装成标准格式并抛出
      const wrappedError = new Error(errorResponse.message);
      (wrappedError as any).response = {
        ...error.response,
        data: errorResponse
      };

      return Promise.reject(wrappedError);
    }
  );

  return instance;
};

// 获取错误消息
const getErrorMessage = (error: AxiosError): string => {
  if (error.response?.data) {
    const data = error.response.data as any;
    
    // 尝试从不同字段获取错误消息
    if (data.detail) return data.detail;
    if (data.message) return data.message;
    if (data.error) return data.error;
    if (typeof data === 'string') return data;
  }

  // 根据状态码返回默认消息
  switch (error.response?.status) {
    case 400:
      return '请求参数错误';
    case 401:
      return '未授权访问';
    case 403:
      return '禁止访问';
    case 404:
      return '请求的资源不存在';
    case 500:
      return '服务器内部错误';
    case 502:
      return '网关错误';
    case 503:
      return '服务暂时不可用';
    case 504:
      return '网关超时';
    default:
      if (error.code === 'ECONNABORTED') {
        return '请求超时，请重试';
      }
      if (error.code === 'ERR_NETWORK') {
        return '网络连接失败，请检查网络';
      }
      return error.message || '未知错误';
  }
};

// 创建API实例
export const apiRequest = createApiInstance();

// 导出便捷方法
export const api = {
  get: <T = any>(url: string, config?: any): Promise<ApiResponse<T>> =>
    apiRequest.get(url, config).then(res => res.data),
    
  post: <T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> =>
    apiRequest.post(url, data, config).then(res => res.data),
    
  put: <T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> =>
    apiRequest.put(url, data, config).then(res => res.data),
    
  delete: <T = any>(url: string, config?: any): Promise<ApiResponse<T>> =>
    apiRequest.delete(url, config).then(res => res.data),
    
  patch: <T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> =>
    apiRequest.patch(url, data, config).then(res => res.data),
};

export default api;
