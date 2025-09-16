import React, { useState } from 'react';
import { 
  Card, 
  Form, 
  Input, 
  Button, 
  TimePicker, 
  Switch, 
  Tabs, 
  Tag, 
  Space, 
  Divider, 
  message, 
  Modal,
  InputNumber,
  Select
} from 'antd';
import { 
  LockOutlined, 
  ClockCircleOutlined, 
  SafetyOutlined, 
  PlusOutlined,
  CloseCircleOutlined
} from '@ant-design/icons';
import type { TabsProps } from 'antd';
import dayjs from 'dayjs';
import { ContentFilters, UsageLimits } from '../types/api';
const { Option } = Select;

// 家长控制页面
const ParentControlPage: React.FC = () => {
  // 密码验证状态
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [pinInput, setPinInput] = useState<string>('');
  const [pinError, setPinError] = useState<string>('');
  
  // 使用时间限制
  const [usageLimits, setUsageLimits] = useState<UsageLimits>({
    user_id: 1,
    daily_limit_minutes: 60,
    weekly_limit_minutes: 300,
    session_limit_minutes: 30,
    restrictions: {
      weekdays: { start: '15:00', end: '18:00' },
      weekends: { start: '10:00', end: '20:00' }
    }
  });
  
  // 内容过滤
  const [contentFilters, setContentFilters] = useState<ContentFilters>({
    user_id: 1,
    filters: {
      blocked_keywords: ['暴力', '色情', '赌博'],
      sensitivity_level: 'medium',
      block_unsafe_content: true,
      notify_parent: true
    },
    message: ''
  });
  
  // 新关键词输入
  const [newKeyword, setNewKeyword] = useState<string>('');
  
  // 修改PIN码模态框
  const [changePinModalVisible, setChangePinModalVisible] = useState<boolean>(false);
  const [newPin, setNewPin] = useState<string>('');
  const [confirmPin, setConfirmPin] = useState<string>('');
  const [currentPin, setCurrentPin] = useState<string>('');
  
  // 默认PIN码 (实际应用中应该从后端获取或使用更安全的方式)
  const [parentPin, setParentPin] = useState<string>('123456');

  // 验证PIN码
  const handlePinVerification = () => {
    if (pinInput === parentPin) {
      setIsAuthenticated(true);
      setPinError('');
      message.success('验证成功，欢迎进入家长控制面板');
      
      // 加载设置数据
      loadSettings();
    } else {
      setPinError('PIN码错误，请重试');
      message.error('PIN码错误，请重试');
    }
  };
  
  // 加载设置
  const loadSettings = async () => {
    try {
      // 实际应用中应该从API获取
      // const usageLimitsData = await ParentControlService.getUsageLimits(1);
      // const contentFiltersData = await ParentControlService.getContentFilters(1);
      
      // setUsageLimits(usageLimitsData);
      // setContentFilters(contentFiltersData);
      
      // 使用模拟数据
      console.log('加载家长控制设置');
    } catch (error) {
      console.error('加载设置失败:', error);
      message.error('加载设置失败，请重试');
    }
  };
  
  // 保存使用时间设置
  const saveUsageLimits = async () => {
    try {
      // 实际应用中应该调用API
      // await ParentControlService.updateUsageLimits(usageLimits);
      
      console.log('保存使用时间设置:', usageLimits);
      message.success('使用时间设置已保存');
    } catch (error) {
      console.error('保存设置失败:', error);
      message.error('保存设置失败，请重试');
    }
  };
  
  // 保存内容过滤设置
  const saveContentFilters = async () => {
    try {
      // 实际应用中应该调用API
      // await ParentControlService.updateContentFilters(contentFilters);
      
      console.log('保存内容过滤设置:', contentFilters);
      message.success('内容过滤设置已保存');
    } catch (error) {
      console.error('保存设置失败:', error);
      message.error('保存设置失败，请重试');
    }
  };
  
  // 添加关键词
  const addKeyword = () => {
    if (newKeyword && newKeyword.trim() !== '') {
      const blockedKeywords = [...(contentFilters.filters.blocked_keywords || [])];
      
      if (!blockedKeywords.includes(newKeyword.trim())) {
        blockedKeywords.push(newKeyword.trim());
        
        setContentFilters({
          ...contentFilters,
          filters: {
            ...contentFilters.filters,
            blocked_keywords: blockedKeywords
          }
        });
        
        setNewKeyword('');
      } else {
        message.warning('该关键词已存在');
      }
    }
  };
  
  // 删除关键词
  const removeKeyword = (keyword: string) => {
    const blockedKeywords = [...(contentFilters.filters.blocked_keywords || [])];
    const updatedKeywords = blockedKeywords.filter((k: string) => k !== keyword);
    
    setContentFilters({
      ...contentFilters,
      filters: {
        ...contentFilters.filters,
        blocked_keywords: updatedKeywords
      }
    });
  };
  
  // 更新使用时间限制
  const updateUsageLimits = (field: string, value: any) => {
    setUsageLimits({
      ...usageLimits,
      [field]: value
    });
  };
  
  // 更新时间段限制
  const updateTimeRestriction = (type: 'weekdays' | 'weekends', field: 'start' | 'end', time: dayjs.Dayjs | null) => {
    if (time) {
      setUsageLimits({
        ...usageLimits,
        restrictions: {
          ...usageLimits.restrictions,
          [type]: {
            ...usageLimits.restrictions[type],
            [field]: time.format('HH:mm')
          }
        }
      });
    }
  };
  
  // 更新内容过滤设置
  const updateContentFilter = (field: string, value: any) => {
    setContentFilters({
      ...contentFilters,
      filters: {
        ...contentFilters.filters,
        [field]: value
      }
    });
  };
  
  // 修改PIN码
  const handleChangePin = () => {
    if (currentPin !== parentPin) {
      message.error('当前PIN码错误');
      return;
    }
    
    if (newPin !== confirmPin) {
      message.error('两次输入的新PIN码不一致');
      return;
    }
    
    if (newPin.length !== 6 || !/^\d+$/.test(newPin)) {
      message.error('PIN码必须是6位数字');
      return;
    }
    
    setParentPin(newPin);
    message.success('PIN码修改成功');
    setChangePinModalVisible(false);
    
    // 清空输入
    setCurrentPin('');
    setNewPin('');
    setConfirmPin('');
  };
  
  // 退出登录
  const handleLogout = () => {
    setIsAuthenticated(false);
    setPinInput('');
  };
  
  // 标签页配置
  const tabItems: TabsProps['items'] = [
    {
      key: '1',
      label: (
        <span>
          <ClockCircleOutlined />
          使用时间管理
        </span>
      ),
      children: (
        <Form layout="vertical">
          <Form.Item label="每日使用时间限制 (分钟)">
            <InputNumber 
              min={1} 
              max={720} 
              value={usageLimits.daily_limit_minutes} 
              onChange={(value) => updateUsageLimits('daily_limit_minutes', value)}
              style={{ width: '100%' }}
            />
          </Form.Item>
          
          <Form.Item label="每周使用时间限制 (分钟)">
            <InputNumber 
              min={1} 
              max={2100} 
              value={usageLimits.weekly_limit_minutes} 
              onChange={(value) => updateUsageLimits('weekly_limit_minutes', value)}
              style={{ width: '100%' }}
            />
          </Form.Item>
          
          <Form.Item label="单次会话时间限制 (分钟)">
            <InputNumber 
              min={1} 
              max={180} 
              value={usageLimits.session_limit_minutes} 
              onChange={(value) => updateUsageLimits('session_limit_minutes', value)}
              style={{ width: '100%' }}
            />
          </Form.Item>
          
          <Divider orientation="left">时间段限制</Divider>
          
          <Form.Item label="工作日允许使用时间段">
            <Space>
              <TimePicker 
                format="HH:mm" 
                value={dayjs(usageLimits.restrictions.weekdays.start, 'HH:mm')} 
                onChange={(time) => updateTimeRestriction('weekdays', 'start', time)}
              />
              <span>至</span>
              <TimePicker 
                format="HH:mm" 
                value={dayjs(usageLimits.restrictions.weekdays.end, 'HH:mm')} 
                onChange={(time) => updateTimeRestriction('weekdays', 'end', time)}
              />
            </Space>
          </Form.Item>
          
          <Form.Item label="周末允许使用时间段">
            <Space>
              <TimePicker 
                format="HH:mm" 
                value={dayjs(usageLimits.restrictions.weekends.start, 'HH:mm')} 
                onChange={(time) => updateTimeRestriction('weekends', 'start', time)}
              />
              <span>至</span>
              <TimePicker 
                format="HH:mm" 
                value={dayjs(usageLimits.restrictions.weekends.end, 'HH:mm')} 
                onChange={(time) => updateTimeRestriction('weekends', 'end', time)}
              />
            </Space>
          </Form.Item>
          
          <Button type="primary" onClick={saveUsageLimits}>
            保存设置
          </Button>
        </Form>
      ),
    },
    {
      key: '2',
      label: (
        <span>
          <SafetyOutlined />
          内容安全过滤
        </span>
      ),
      children: (
        <Form layout="vertical">
          <Form.Item label="敏感度级别">
            <Select 
              value={contentFilters.filters.sensitivity_level} 
              onChange={(value) => updateContentFilter('sensitivity_level', value)}
              style={{ width: '100%' }}
            >
              <Option value="low">低 (仅过滤极端内容)</Option>
              <Option value="medium">中 (过滤大部分不适内容)</Option>
              <Option value="high">高 (严格过滤所有可能不适内容)</Option>
            </Select>
          </Form.Item>
          
          <Form.Item label="屏蔽不安全内容">
            <Switch 
              checked={contentFilters.filters.block_unsafe_content} 
              onChange={(checked) => updateContentFilter('block_unsafe_content', checked)}
            />
          </Form.Item>
          
          <Form.Item label="发现不安全内容时通知家长">
            <Switch 
              checked={contentFilters.filters.notify_parent} 
              onChange={(checked) => updateContentFilter('notify_parent', checked)}
            />
          </Form.Item>
          
          <Divider orientation="left">关键词过滤</Divider>
          
          <Form.Item label="添加屏蔽关键词">
            <Space>
              <Input 
                placeholder="输入关键词" 
                value={newKeyword} 
                onChange={(e) => setNewKeyword(e.target.value)}
                onPressEnter={addKeyword}
              />
              <Button type="primary" icon={<PlusOutlined />} onClick={addKeyword}>
                添加
              </Button>
            </Space>
          </Form.Item>
          
          <div style={{ marginBottom: 16 }}>
            {contentFilters.filters.blocked_keywords?.map((keyword: string) => (
              <Tag 
                key={keyword} 
                closable 
                onClose={() => removeKeyword(keyword)}
                style={{ margin: '0 8px 8px 0' }}
              >
                {keyword}
              </Tag>
            ))}
          </div>
          
          <Button type="primary" onClick={saveContentFilters}>
            保存设置
          </Button>
        </Form>
      ),
    },
    {
      key: '3',
      label: (
        <span>
          <LockOutlined />
          安全设置
        </span>
      ),
      children: (
        <div>
          <Button 
            type="primary" 
            onClick={() => setChangePinModalVisible(true)}
            style={{ marginBottom: 16 }}
          >
            修改PIN码
          </Button>
          
          <Divider />
          
          <Button danger onClick={handleLogout}>
            退出家长控制面板
          </Button>
        </div>
      ),
    },
  ];

  // PIN码修改模态框
  const changePinModal = (
    <Modal
      title="修改PIN码"
      open={changePinModalVisible}
      onOk={handleChangePin}
      onCancel={() => setChangePinModalVisible(false)}
      okText="确认修改"
      cancelText="取消"
    >
      <Form layout="vertical">
        <Form.Item label="当前PIN码" required>
          <Input.Password 
            placeholder="请输入当前PIN码" 
            value={currentPin} 
            onChange={(e) => setCurrentPin(e.target.value)}
            maxLength={6}
          />
        </Form.Item>
        
        <Form.Item label="新PIN码" required help="PIN码必须是6位数字">
          <Input.Password 
            placeholder="请输入新PIN码" 
            value={newPin} 
            onChange={(e) => setNewPin(e.target.value)}
            maxLength={6}
          />
        </Form.Item>
        
        <Form.Item label="确认新PIN码" required>
          <Input.Password 
            placeholder="请再次输入新PIN码" 
            value={confirmPin} 
            onChange={(e) => setConfirmPin(e.target.value)}
            maxLength={6}
          />
        </Form.Item>
      </Form>
    </Modal>
  );

  // 渲染验证页面或控制面板
  return (
    <div style={{ padding: '20px' }}>
      {!isAuthenticated ? (
        <Card 
          title={
            <div style={{ textAlign: 'center' }}>
              <LockOutlined style={{ marginRight: 8 }} />
              家长控制验证
            </div>
          }
          style={{ maxWidth: 400, margin: '0 auto' }}
        >
          <Form layout="vertical">
            <Form.Item 
              label="请输入6位PIN码" 
              validateStatus={pinError ? 'error' : ''}
              help={pinError}
            >
              <Input.Password 
                placeholder="请输入PIN码" 
                value={pinInput} 
                onChange={(e) => setPinInput(e.target.value)}
                maxLength={6}
                onPressEnter={handlePinVerification}
              />
            </Form.Item>
            
            <Form.Item>
              <Button 
                type="primary" 
                block 
                onClick={handlePinVerification}
              >
                验证
              </Button>
            </Form.Item>
          </Form>
        </Card>
      ) : (
        <Card 
          title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>家长控制面板</span>
              <Button 
                icon={<CloseCircleOutlined />} 
                onClick={handleLogout}
                danger
                size="small"
              >
                退出
              </Button>
            </div>
          }
        >
          <Tabs defaultActiveKey="1" items={tabItems} />
          {changePinModal}
        </Card>
      )}
    </div>
  );
};

export default ParentControlPage;