import React from 'react';
import { Layout as AntLayout, Menu } from 'antd';
// import { 
//   MessageOutlined, 
//   UserOutlined,
//   AudioOutlined 
// } from '@ant-design/icons';

const { Header, Sider, Content } = AntLayout;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider 
        theme="light" 
        width={10}
        style={{
          boxShadow: '2px 0 6px rgba(0,21,41,0.1)',
        }}
      >
        <div style={{ 
          padding: '16px', 
          textAlign: 'center',
          fontWeight: 'bold',
          borderBottom: '1px solid #f0f0f0'
        }}>
          {/* Happy Partner */}
        </div>
        
        {/* <Menu
          mode="inline"
          defaultSelectedKeys={['chat']}
          items={[
            {
              key: 'chat',
              icon: <MessageOutlined />,
              label: '聊天',
            },
            {
              key: 'audio',
              icon: <AudioOutlined />,
              label: '音频',
            },
            {
              key: 'profile',
              icon: <UserOutlined />,
              label: '个人中心',
            },
          ]}
        /> */}
      </Sider>
      
      <AntLayout>
        <Header style={{ 
          padding: '0 24px', 
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 1px 4px rgba(0,21,41,0.1)'
        }}>
          <h2 style={{ margin: 0, color: '#1890ff' }}>儿童教育AI助手</h2>
          <div style={{ color: '#666' }}>欢迎使用</div>
        </Header>
        
        <Content style={{ 
          margin: '24px', 
          padding: '24px', 
          background: '#fff',
          borderRadius: '6px',
          minHeight: 280
        }}>
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;