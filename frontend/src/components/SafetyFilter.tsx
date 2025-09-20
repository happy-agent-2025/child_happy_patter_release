import React, { useEffect, useState } from 'react';
import { Modal, Alert, Button, Typography } from 'antd';
import { WarningOutlined } from '@ant-design/icons';
import { ParentControlService } from '../services/parentControlApi';

const { Text, Paragraph } = Typography;

interface SafetyFilterProps {
  content: string;
  onFilterComplete: (filteredContent: string, isSafe: boolean) => void;
  userId?: number;
}

const SafetyFilter: React.FC<SafetyFilterProps> = ({ 
  content, 
  onFilterComplete,
  userId = 1 // 默认用户ID
}) => {
  // 不再使用 isChecking 状态
  const [, setIsChecking] = useState<boolean>(true);
  const [isSafe, setIsSafe] = useState<boolean>(true);
  const [filteredContent, setFilteredContent] = useState<string>(content);
  const [reason, setReason] = useState<string>('');
  const [showModal, setShowModal] = useState<boolean>(false);
  
  // 模拟的关键词列表 (实际应用中应从API获取)
  const [blockedKeywords, setBlockedKeywords] = useState<string[]>([
    '暴力', '色情', '赌博', '毒品', '自杀', '恐怖', '歧视'
  ]);
  
  // 从API获取内容过滤设置
  useEffect(() => {
    const fetchContentFilters = async () => {
      try {
        // 实际应用中应该从API获取
        // const filters = await ParentControlService.getContentFilters(userId);
        // if (filters.filters.blocked_keywords) {
        //   setBlockedKeywords(filters.filters.blocked_keywords);
        // }
        
        // 使用模拟数据
        console.log('加载内容过滤设置');
      } catch (error) {
        console.error('获取内容过滤设置失败:', error);
      }
    };
    
    fetchContentFilters();
  }, [userId]);
  
  // 检查内容安全性
  useEffect(() => {
    const checkContentSafety = async () => {
      // 使用简单的关键词过滤模拟安全检查
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
      
      setIsSafe(isContentSafe);
      setFilteredContent(filteredText);
      
      if (!isContentSafe) {
        setReason(`检测到不适宜内容: ${detectedKeywords.join(', ')}`);
        setShowModal(true);
      }
      
      // 无论安全与否，都返回过滤后的内容
      onFilterComplete(filteredText, isContentSafe);
    };
    
    if (content) {
      checkContentSafety();
    }
  }, [content, blockedKeywords, onFilterComplete]);
  
  // 处理模态框关闭
  const handleModalClose = () => {
    setShowModal(false);
  };
  
  // 不安全内容提示模态框
  const unsafeContentModal = (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center', color: '#ff4d4f' }}>
          <WarningOutlined style={{ marginRight: 8 }} />
          检测到不适宜内容
        </div>
      }
      open={showModal}
      onCancel={handleModalClose}
      footer={[
        <Button key="ok" type="primary" danger onClick={handleModalClose}>
          我知道了
        </Button>
      ]}
    >
      <Alert
        message="内容已被过滤"
        description={reason}
        type="warning"
        showIcon
        style={{ marginBottom: 16 }}
      />
      
      <Paragraph>
        <Text strong>原始内容:</Text>
        <div style={{ 
          padding: 8, 
          backgroundColor: '#fff2f0', 
          border: '1px solid #ffccc7',
          borderRadius: 4,
          marginTop: 8
        }}>
          {content}
        </div>
      </Paragraph>
      
      <Paragraph>
        <Text strong>过滤后内容:</Text>
        <div style={{ 
          padding: 8, 
          backgroundColor: '#f6ffed', 
          border: '1px solid #b7eb8f',
          borderRadius: 4,
          marginTop: 8
        }}>
          {filteredContent}
        </div>
      </Paragraph>
    </Modal>
  );
  
  // 组件不渲染任何可见内容，只在检测到不安全内容时显示模态框
  return (
    <>
      {unsafeContentModal}
    </>
  );
};

export default SafetyFilter;