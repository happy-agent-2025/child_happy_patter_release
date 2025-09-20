import { apiRequest, API_ENDPOINTS } from './api';
import { ContentFilters, UsageLimits } from '../types/api';

// 家长控制API服务类
export class ParentControlService {
  
  /**
   * 验证家长PIN码
   */
  static async verifyParentPin(pin: string): Promise<boolean> {
    try {
      const response = await apiRequest.post(
        API_ENDPOINTS.PARENT_CONTROL.VERIFY_PIN, 
        { pin }
      );
      
      console.log('[ParentControl] PIN码验证成功');
      return response.verified;
    } catch (error: any) {
      console.error('[ParentControl] PIN码验证失败:', error.response?.data?.detail || error.message);
      return false;
    }
  }

  /**
   * 更新家长PIN码
   */
  static async updateParentPin(currentPin: string, newPin: string): Promise<boolean> {
    try {
      const response = await apiRequest.post(
        API_ENDPOINTS.PARENT_CONTROL.UPDATE_PIN, 
        { current_pin: currentPin, new_pin: newPin }
      );
      
      console.log('[ParentControl] PIN码更新成功');
      return response.success;
    } catch (error: any) {
      console.error('[ParentControl] PIN码更新失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || 'PIN码更新失败');
    }
  }

  /**
   * 获取内容过滤设置
   */
  static async getContentFilters(userId: number): Promise<ContentFilters> {
    try {
      const response = await apiRequest.get<ContentFilters>(
        API_ENDPOINTS.USERS.CONTENT_FILTERS(userId)
      );
      
      console.log('[ParentControl] 获取内容过滤设置成功');
      return response;
    } catch (error: any) {
      console.error('[ParentControl] 获取内容过滤设置失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '获取内容过滤设置失败');
    }
  }

  /**
   * 更新内容过滤设置
   */
  static async updateContentFilters(filters: ContentFilters): Promise<ContentFilters> {
    try {
      const response = await apiRequest.put<ContentFilters>(
        API_ENDPOINTS.USERS.CONTENT_FILTERS(filters.user_id),
        filters
      );
      
      console.log('[ParentControl] 更新内容过滤设置成功');
      return response;
    } catch (error: any) {
      console.error('[ParentControl] 更新内容过滤设置失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '更新内容过滤设置失败');
    }
  }

  /**
   * 获取使用时间限制
   */
  static async getUsageLimits(userId: number): Promise<UsageLimits> {
    try {
      const response = await apiRequest.get<UsageLimits>(
        API_ENDPOINTS.USERS.USAGE_LIMITS(userId)
      );
      
      console.log('[ParentControl] 获取使用时间限制成功');
      return response;
    } catch (error: any) {
      console.error('[ParentControl] 获取使用时间限制失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '获取使用时间限制失败');
    }
  }

  /**
   * 更新使用时间限制
   */
  static async updateUsageLimits(limits: UsageLimits): Promise<UsageLimits> {
    try {
      const response = await apiRequest.put<UsageLimits>(
        API_ENDPOINTS.USERS.USAGE_LIMITS(limits.user_id),
        limits
      );
      
      console.log('[ParentControl] 更新使用时间限制成功');
      return response;
    } catch (error: any) {
      console.error('[ParentControl] 更新使用时间限制失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '更新使用时间限制失败');
    }
  }

  /**
   * 获取安全日志
   */
  static async getSecurityLogs(userId: number): Promise<any> {
    try {
      const response = await apiRequest.get(
        API_ENDPOINTS.USERS.SECURITY_LOGS(userId)
      );
      
      console.log('[ParentControl] 获取安全日志成功');
      return response;
    } catch (error: any) {
      console.error('[ParentControl] 获取安全日志失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '获取安全日志失败');
    }
  }
}