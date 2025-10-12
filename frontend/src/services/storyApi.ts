import { apiRequest, API_ENDPOINTS } from './api';

// 故事创作请求类型
export interface StoryRequest {
  user_id: string;
  content: string;
  session_id?: string;
}

// 故事创作响应类型
export interface StoryResponse {
  response: string;
  metadata: Record<string, any>;
  story_world: Record<string, any>;
  roles: Record<string, any>;
  story_history: any[];
  relevant_memories: any[];
  creation_mode: string;
}

// 故事世界创建请求
export interface StoryWorldRequest {
  user_id: string;
  world_name: string;
  world_type: string;
  background: string;
  rules: string;
  suggested_roles: string[];
}

// 故事系统状态
export interface StorySystemStatus {
  system_name: string;
  version: string;
  mem0_status: string;
  langgraph_status: string;
  available_features: string[];
  mem0_test?: string;
}

// 故事创作API服务类
export class StoryApiService {

  /**
   * 创建故事/角色扮演
   */
  static async createStory(storyData: StoryRequest): Promise<StoryResponse> {
    try {
      // 直接使用axios请求，避免拦截器的问题
      const response = await apiRequest.post(
        '/api/story/create',
        storyData
      );

      console.log('[Story] 故事创作成功');
      return response.data || response;
    } catch (error: any) {
      console.error('[Story] 故事创作失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '故事创作失败，请重试');
    }
  }

  /**
   * 创建故事世界
   */
  static async createStoryWorld(worldData: StoryWorldRequest): Promise<any> {
    try {
      const response = await apiRequest.post(
        '/api/story/world/create',
        worldData
      );

      console.log('[Story] 故事世界创建成功');
      return response.data;
    } catch (error: any) {
      console.error('[Story] 故事世界创建失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '故事世界创建失败，请重试');
    }
  }

  /**
   * 获取故事历史
   */
  static async getStoryHistory(userId: string, limit: number = 10): Promise<any> {
    try {
      const response = await apiRequest.get(
        `/api/story/history/${userId}?limit=${limit}`
      );

      console.log('[Story] 获取故事历史成功');
      return response.data;
    } catch (error: any) {
      console.error('[Story] 获取故事历史失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '获取故事历史失败');
    }
  }

  /**
   * 搜索故事记忆
   */
  static async searchStoryMemories(userId: string, query: string, limit: number = 5): Promise<any> {
    try {
      const response = await apiRequest.post(
        '/api/story/memory/search',
        {
          user_id: userId,
          query,
          limit
        }
      );

      console.log('[Story] 记忆搜索成功');
      return response.data;
    } catch (error: any) {
      console.error('[Story] 记忆搜索失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '记忆搜索失败');
    }
  }

  /**
   * 获取用户的故事世界列表
   */
  static async getUserStoryWorlds(userId: string): Promise<any> {
    try {
      const response = await apiRequest.get(
        `/api/story/worlds/${userId}`
      );

      console.log('[Story] 获取故事世界列表成功');
      return response.data;
    } catch (error: any) {
      console.error('[Story] 获取故事世界列表失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '获取故事世界列表失败');
    }
  }

  /**
   * 清除用户的故事记忆
   */
  static async clearUserMemories(userId: string): Promise<any> {
    try {
      const response = await apiRequest.delete(
        `/api/story/memory/${userId}`
      );

      console.log('[Story] 清除记忆成功');
      return response.data;
    } catch (error: any) {
      console.error('[Story] 清除记忆失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '清除记忆失败');
    }
  }

  /**
   * 获取故事系统状态
   */
  static async getSystemStatus(): Promise<StorySystemStatus> {
    try {
      const response = await apiRequest.get<StorySystemStatus>(
        '/api/story/status'
      );

      console.log('[Story] 获取系统状态成功');
      return response.data;
    } catch (error: any) {
      console.error('[Story] 获取系统状态失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '获取系统状态失败');
    }
  }

  /**
   * 健康检查
   */
  static async healthCheck(): Promise<any> {
    try {
      const response = await apiRequest.get(
        '/api/story/health'
      );

      console.log('[Story] 健康检查成功');
      return response.data;
    } catch (error: any) {
      console.error('[Story] 健康检查失败:', error.response?.data?.detail || error.message);
      throw new Error(error.response?.data?.detail || '健康检查失败');
    }
  }

  /**
   * 智能故事创作（根据内容自动判断是创建世界还是角色扮演）
   */
  static async intelligentStory(message: string, userId: string = '1', sessionId?: string): Promise<StoryResponse> {
    const storyData: StoryRequest = {
      user_id: userId,
      content: message,
      session_id: sessionId
    };

    return this.createStory(storyData);
  }

  /**
   * 获取儿童友好的故事世界列表
   */
  static getKidFriendlyWorlds() {
    return [
      {
        id: "magic_forest",
        name: "魔法森林",
        description: "一个充满神奇动物的森林，小动物们都会魔法！",
        icon: "🌲",
        color: "#4CAF50"
      },
      {
        id: "ocean_adventure",
        name: "海底世界",
        description: "美丽的大海深处，有很多可爱的海洋朋友！",
        icon: "🌊",
        color: "#2196F3"
      },
      {
        id: "space_adventure",
        name: "太空冒险",
        description: "在星星之间旅行，和外星朋友一起玩耍！",
        icon: "🚀",
        color: "#9C27B0"
      },
      {
        id: "dinosaur_world",
        name: "恐龙乐园",
        description: "和友善的小恐龙们一起在史前世界玩耍！",
        icon: "🦕",
        color: "#FF9800"
      },
      {
        id: "princess_castle",
        name: "公主城堡",
        description: "美丽的城堡里，有公主、王子和神奇的魔法！",
        icon: "🏰",
        color: "#E91E63"
      },
      {
        id: "happy_farm",
        name: "快乐农场",
        description: "热闹的农场里，小动物们每天都过得很开心！",
        icon: "🚜",
        color: "#8BC34A"
      }
    ];
  }

  /**
   * 获取儿童角色选择
   */
  static getRoleChoices(worldId: string) {
    const roleMap = {
      "magic_forest": ["小魔法师", "勇敢的小兔子", "聪明的小狐狸", "会飞的小鸟"],
      "ocean_adventure": ["小美人鱼", "勇敢的小海龟", "聪明的小章鱼", "友好的鲨鱼"],
      "space_adventure": ["小宇航员", "可爱的外星人", "聪明的机器人", "勇敢的太空猫"],
      "dinosaur_world": ["小霸王龙", "温和的三角龙", "会飞的翼龙", "聪明的小人类"],
      "princess_castle": ["小公主", "勇敢的王子", "神奇的小仙女", "友好的小龙"],
      "happy_farm": ["农场小主人", "聪明的小猪", "可爱的小羊", "勤劳的小鸡"]
    };

    return roleMap[worldId] || ["勇敢的小英雄", "聪明的小伙伴", "神奇的小动物"];
  }

  /**
   * 儿童友好的鼓励语
   */
  static getKidFriendlyEncouragement() {
    const encouragements = [
      "太棒了！你真是个小天才！",
      "哇！你的想象力真丰富！",
      "真厉害！继续加油哦！",
      "你真棒！我喜欢你的想法！",
      "太有趣了！还有什么呢？",
      "你真是个创意小达人！",
      "哇哦！这个想法太棒了！",
      "你真聪明！继续讲故事吧！"
    ];

    return encouragements[Math.floor(Math.random() * encouragements.length)];
  }
}