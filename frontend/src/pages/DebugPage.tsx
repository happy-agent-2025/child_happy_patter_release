import { useState } from 'react';
import { Card, Button, Typography, message } from 'antd';
import { ChatApiService } from '../services/chatApi';

const { Title, Text } = Typography;

const DebugPage: React.FC = () => {
  const [log, setLog] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const addLog = (msg: string) => {
    setLog(prev => [...prev, `${new Date().toLocaleTimeString()}: ${msg}`]);
  };

  const testConnection = async () => {
    setLoading(true);
    addLog('开始测试连接...');
    
    try {
      addLog('调用 ChatApiService.intelligentChat...');
      const response = await ChatApiService.intelligentChat('测试连接消息', 1);
      
      addLog(`API调用成功！响应类型: ${typeof response}`);
      addLog(`响应键: ${Object.keys(response).join(', ')}`);
      addLog(`代理: ${response.agent}`);
      addLog(`是否有response字段: ${!!response.response}`);
      addLog(`是否有answer字段: ${!!response.answer}`);
      addLog(`是否有message字段: ${!!response.message}`);
      
      const content = response.response || response.answer || response.message || '无内容';
      addLog(`最终内容: ${content.substring(0, 50)}...`);
      
      message.success('连接测试成功！');
      
    } catch (error: any) {
      addLog(`❌ 连接测试失败: ${error.message}`);
      addLog(`错误详情: ${JSON.stringify({
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        headers: error.response?.headers
      }, null, 2)}`);
      
      message.error('连接测试失败');
    } finally {
      setLoading(false);
    }
  };

  const clearLog = () => {
    setLog([]);
  };

  return (
    <div style={{ padding: '20px' }}>
      <Title level={2}>调试页面</Title>
      
      <Card style={{ marginBottom: '20px' }}>
        <Button 
          type="primary" 
          onClick={testConnection}
          loading={loading}
          style={{ marginRight: '10px' }}
        >
          测试API连接
        </Button>
        <Button onClick={clearLog}>
          清除日志
        </Button>
      </Card>

      <Card title="调试日志">
        <div style={{ height: '400px', overflowY: 'auto', fontFamily: 'monospace', fontSize: '12px' }}>
          {log.length === 0 ? (
            <Text type="secondary">暂无日志，点击"测试API连接"开始调试</Text>
          ) : (
            log.map((entry, index) => (
              <div key={index} style={{ marginBottom: '4px' }}>
                {entry}
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  );
};

export default DebugPage;