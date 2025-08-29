import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: '/api', // 使用相对路径，通过Vite代理转发到后端
  timeout: 100000,
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
  },
  // 添加响应数据类型转换
  transformResponse: [(data) => {
    if (typeof data === 'string') {
      try {
        return JSON.parse(data);
      } catch (e) {
        return data;
      }
    }
    return data;
  }]
});

// 请求拦截器
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从localStorage获取JWT令牌
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 添加请求时间戳
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url} - ${new Date().toISOString()}`);
    
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`[API Response] ${response.status} ${response.config.url} - ${new Date().toISOString()}`);
    console.log('[API Response Data]', response.data);
    return response;
  },
  (error) => {
    console.error('[API Response Error] 详细错误信息:', {
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
    
    // 处理401未授权错误
    if (error.response?.status === 401) {
      // 清除本地存储的令牌
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      
      // 重定向到登录页面
      window.location.href = '/login';
    }
    
    // 处理网络错误
    if (!error.response) {
      error.message = '网络连接错误，请检查您的网络设置';
    }
    
    return Promise.reject(error);
  }
);

export default api;

// 导出常用的HTTP方法
export const apiRequest = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => 
    api.get(url, config).then(response => response.data),
    
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => 
    api.post(url, data, { 
      ...config,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        ...config?.headers
      }
    }).then(response => response.data),
    
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => 
    api.put(url, data, { 
      ...config,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        ...config?.headers
      }
    }).then(response => response.data),
    
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => 
    api.delete(url, config).then(response => response.data),
    
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => 
    api.patch(url, data, { 
      ...config,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        ...config?.headers
      }
    }).then(response => response.data),
};

// API端点常量
export const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    ME: '/auth/me',
  },
  
  // 聊天相关
  CHAT: {
    SEND: '/chat',
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
};