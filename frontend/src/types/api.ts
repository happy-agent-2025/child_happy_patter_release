// 认证相关类型
export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
  is_active: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  created_at: string;
  is_active: boolean;
}

// 聊天相关类型
export interface ChatRequest {
  user_id?: number;
  session_id?: number;
  content: string;
}

export interface SafetyCheckRequest {
  user_id?: number;
  content: string;
}

export interface SafetyCheckResponse {
  is_safe: boolean;
  reason: string;
  confidence: number;
  suggested_content?: string;
}

export interface EduQuestionRequest {
  user_id?: number;
  question: string;
  grade_level?: string;
}

export interface EduQuestionResponse {
  answer: string;
  explanation?: string;
  related_topics?: string[];
  difficulty_level?: string;
}

export interface EmotionSupportRequest {
  user_id?: number;
  content: string;
  emotion_type?: string;
}

export interface EmotionSupportResponse {
  response: string;
  support_type: string;
  suggested_activities?: string[];
  follow_up_questions?: string[];
}

// 音频相关类型
export interface AudioTranscribeRequest {
  file: File;
  preprocess?: boolean;
}

export interface AudioTranscribeResponse {
  text: string;
  confidence: number;
  duration: number;
  language: string;
}

export interface AudioSynthesizeRequest {
  text: string;
  voice_type?: 'female' | 'male';
  speed?: number;
  volume?: number;
}

export interface AudioSynthesizeResponse {
  audio_data: string;
  duration: number;
  format: string;
  sample_rate: number;
}

export interface AudioProcessRequest {
  file: File;
  target_rate?: number;
  target_rms?: number;
  silence_threshold?: number;
}

export interface AudioProcessResponse {
  processed_audio: string;
  original_duration: number;
  processed_duration: number;
  sample_rate: number;
  processing_steps: string[];
}

// 声纹相关类型
export interface VoiceRegisterRequest {
  user_id: number;
  audio_data: string;
  sample_rate?: number;
  audio_duration?: number;
}

export interface VoiceRegisterResponse {
  success: boolean;
  user_id: number;
  feature_dimension: number;
  message: string;
}

export interface VoiceVerifyRequest {
  user_id: number;
  audio_data: string;
  sample_rate?: number;
  threshold?: number;
  audio_duration?: number;
}

export interface VoiceVerifyResponse {
  verified: boolean;
  similarity: number;
  user_id: number;
  threshold: number;
  confidence: number;
}

// 记忆管理类型
export interface MemoryActionRequest {
  action: 'store' | 'retrieve' | 'delete';
  user_id?: number;
  session_id?: number;
  content?: string;
  memory_key?: string;
  memory_type?: string;
}

export interface MemoryActionResponse {
  success: boolean;
  action: string;
  memory_data: any;
  message: string;
  timestamp: string;
}

// 会话管理类型
export interface Session {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface SessionCreateRequest {
  title?: string;
}

// 对话历史类型
export interface ConversationItem {
  id: number;
  user_id: number;
  session_id?: number;
  agent_type: string;
  conversation_history: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationListResponse {
  user_id: number;
  conversations: ConversationItem[];
}

// 安全日志类型
export interface SecurityLogItem {
  id: number;
  content: string;
  is_safe: boolean;
  filtered_content?: string;
  created_at: string;
}

export interface SecurityLogListResponse {
  user_id: number;
  security_logs: SecurityLogItem[];
}

// 用户统计类型
export interface UserActivityStats {
  user_id: number;
  period_days: number;
  statistics: {
    total_conversations: number;
    agent_usage: Record<string, number>;
    daily_activity: Record<string, number>;
    security_stats: {
      unsafe_content_count: number;
      total_security_logs: number;
    };
  };
}

export interface LearningProgress {
  user_id: number;
  total_questions: number;
  subjects: Record<string, any>;
  progress_summary: {
    total_questions: number;
    engagement_level: 'low' | 'medium' | 'high';
  };
}

// 家长控制类型
export interface ContentFilters {
  user_id: number;
  filters: Record<string, any>;
  message: string;
}

export interface UsageLimits {
  user_id: number;
  daily_limit_minutes: number;
  weekly_limit_minutes: number;
  session_limit_minutes: number;
  restrictions: {
    weekdays: { start: string; end: string };
    weekends: { start: string; end: string };
  };
}

// 通用响应类型
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

export interface ApiError {
  message: string;
  status?: number;
  code?: string;
}