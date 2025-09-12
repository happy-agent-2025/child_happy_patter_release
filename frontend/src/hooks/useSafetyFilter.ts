import { useState, useCallback } from 'react';

export interface UseSafetyFilterReturn {
  safetyFilterEnabled: boolean;
  toggleSafetyFilter: () => void;
  filterContent: (content: string) => Promise<{ content: string; isSafe: boolean; reason?: string }>;
}

export const useSafetyFilter = (): UseSafetyFilterReturn => {
  const [safetyFilterEnabled, setSafetyFilterEnabled] = useState<boolean>(true);

  const toggleSafetyFilter = useCallback(() => {
    setSafetyFilterEnabled(prev => !prev);
  }, []);

  const filterContent = useCallback(async (content: string) => {
    if (!safetyFilterEnabled) {
      return { content, isSafe: true };
    }

    // 模拟的关键词列表
    const blockedKeywords = [
      '暴力', '色情', '赌博', '毒品', '自杀', '恐怖', '歧视'
    ];

    let isContentSafe = true;
    let detectedKeywords: string[] = [];
    let filteredText = content;

    blockedKeywords.forEach(keyword => {
      if (content.includes(keyword)) {
        isContentSafe = false;
        detectedKeywords.push(keyword);
        
        // 用星号替换敏感词
        const stars = '*'.repeat(keyword.length);
        filteredText = filteredText.replace(new RegExp(keyword, 'g'), stars);
      }
    });

    const result = {
      content: filteredText,
      isSafe: isContentSafe,
      reason: detectedKeywords.length > 0 ? `检测到不适宜内容: ${detectedKeywords.join(', ')}` : undefined
    };

    return result;
  }, [safetyFilterEnabled]);

  return {
    safetyFilterEnabled,
    toggleSafetyFilter,
    filterContent,
  };
};