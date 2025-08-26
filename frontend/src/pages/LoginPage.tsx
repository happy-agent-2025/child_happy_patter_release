import React from 'react';
import { Card, Form, Input, Button } from 'antd';

const LoginPage: React.FC = () => {
  const onFinish = (values: any) => {
    console.log('登录信息:', values);
    // 这里后续会集成登录API
  };

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      background: '#f0f2f5'
    }}>
      <Card title="用户登录" style={{ width: 400 }}>
        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          layout="vertical"
        >
          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, message: '请输入用户名!' }]}
          >
            <Input placeholder="请输入用户名" />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: '请输入密码!' }]}
          >
            <Input.Password placeholder="请输入密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" style={{ width: '100%' }}>
              登录
            </Button>
          </Form.Item>
        </Form>
        
        <div style={{ 
          textAlign: 'center', 
          color: '#999', 
          fontSize: '12px',
          marginTop: '20px'
        }}>
          演示版本 - 任意用户名密码即可登录
        </div>
      </Card>
    </div>
  );
};

export default LoginPage;