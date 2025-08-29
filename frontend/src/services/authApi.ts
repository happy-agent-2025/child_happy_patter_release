import { apiRequest, API_ENDPOINTS } from './api';
import { 
  LoginRequest, 
  RegisterRequest, 
  Token, 
  UserResponse 
} from '../types/api';

// 认证API服务类
export class AuthApiService {
  
  /**
   * 用户登录
   */
  static async login(credentials: LoginRequest): Promise<Token> {
    try {
      const response = await apiRequest.post<Token>(
        API_ENDPOINTS.AUTH.LOGIN, 
        credentials
      );
      
      // 登录成功后存储令牌
      if (response.access_token) {
        localStorage.setItem('access_token', response.access_token);
        console.log('[Auth] 登录成功，令牌已存储');
      }
      
      return response;
    } catch (error: any) {
      console.error('[Auth] 登录失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '登录失败，请检查用户名和密码');
    }
  }

  /**
   * 用户注册
   */
  static async register(userData: RegisterRequest): Promise<UserResponse> {
    try {
      const response = await apiRequest.post<UserResponse>(
        API_ENDPOINTS.AUTH.REGISTER, 
        userData
      );
      
      console.log('[Auth] 注册成功');
      return response;
    } catch (error: any) {
      console.error('[Auth] 注册失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '注册失败，请重试');
    }
  }

  /**
   * 获取当前用户信息
   */
  static async getCurrentUser(): Promise<UserResponse> {
    try {
      const response = await apiRequest.get<UserResponse>(API_ENDPOINTS.AUTH.ME);
      
      // 存储用户信息到本地存储
      localStorage.setItem('user_info', JSON.stringify(response));
      console.log('[Auth] 用户信息获取成功');
      
      return response;
    } catch (error: any) {
      console.error('[Auth] 获取用户信息失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '获取用户信息失败');
    }
  }

  /**
   * 用户登出
   */
  static logout(): void {
    // 清除本地存储
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    console.log('[Auth] 用户已登出');
  }

  /**
   * 检查是否已登录
   */
  static isLoggedIn(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token;
  }

  /**
   * 获取存储的用户信息
   */
  static getStoredUserInfo(): UserResponse | null {
    try {
      const userInfo = localStorage.getItem('user_info');
      return userInfo ? JSON.parse(userInfo) : null;
    } catch (error) {
      console.error('[Auth] 解析用户信息失败:', error);
      return null;
    }
  }

  /**
   * 获取存储的访问令牌
   */
  static getStoredToken(): string | null {
    return localStorage.getItem('access_token');
  }
}