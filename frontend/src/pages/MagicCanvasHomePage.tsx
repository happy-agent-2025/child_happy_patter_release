import React, { useState } from 'react';
import { Button, Card, Typography, Space, Progress, Modal, Upload } from 'antd';
import { 
  CameraOutlined, 
  UploadOutlined, 
  PlayCircleOutlined,
  EditOutlined,
  SoundOutlined,
  ShareAltOutlined,
  CloudUploadOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

const MagicCanvasHomePage: React.FC = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [isModalVisible, setIsModalVisible] = useState(false);

  const handleScan = () => {
    setIsScanning(true);
    setScanProgress(0);
    
    // 模拟扫描过程
    const interval = setInterval(() => {
      setScanProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsScanning(false);
          setIsModalVisible(true);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
  };

  return (
    <div style={{ 
      padding: '20px', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* 头部标题 */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <Title level={1} style={{ 
            color: 'white', 
            fontSize: '3rem',
            textShadow: '2px 2px 4px rgba(0,0,0,0.3)'
          }}>
            🎨 画境奇缘 MagicCanvas Tales
          </Title>
          <Text style={{ 
            color: 'rgba(255,255,255,0.9)', 
            fontSize: '1.2rem',
            display: 'block',
            marginTop: '10px'
          }}>
            "你画世界，我来动情" - 将静态画作转化为可交互的动态童话
          </Text>
        </div>

        {/* 主要功能卡片 */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
          gap: '20px',
          marginBottom: '40px'
        }}>
          {/* 画布扫描 */}
          <Card 
            hoverable 
            style={{ 
              borderRadius: '15px',
              textAlign: 'center',
              background: 'rgba(255,255,255,0.9)',
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
            }}
          >
            <CameraOutlined style={{ fontSize: '3rem', color: '#667eea' }} />
            <Title level={3} style={{ marginTop: '15px' }}>画布扫描</Title>
            <Text style={{ display: 'block', marginBottom: '20px' }}>
              拍照识别画作中的角色、场景和物体
            </Text>
            <Button 
              type="primary" 
              size="large" 
              onClick={handleScan}
              disabled={isScanning}
              style={{ 
                background: '#667eea',
                borderColor: '#667eea'
              }}
            >
              {isScanning ? '扫描中...' : '开始扫描'}
            </Button>
            {isScanning && (
              <div style={{ marginTop: '15px' }}>
                <Progress percent={scanProgress} showInfo />
              </div>
            )}
          </Card>

          {/* 编辑工作台 */}
          <Card 
            hoverable 
            style={{ 
              borderRadius: '15px',
              textAlign: 'center',
              background: 'rgba(255,255,255,0.9)',
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
            }}
          >
            <EditOutlined style={{ fontSize: '3rem', color: '#f093fb' }} />
            <Title level={3} style={{ marginTop: '15px' }}>编辑工作台</Title>
            <Text style={{ display: 'block', marginBottom: '20px' }}>
              为角色添加动作、表情和对话
            </Text>
            <Button 
              type="primary" 
              size="large"
              style={{ 
                background: '#f093fb',
                borderColor: '#f093fb'
              }}
            >
              进入编辑
            </Button>
          </Card>

          {/* 故事剧场 */}
          <Card 
            hoverable 
            style={{ 
              borderRadius: '15px',
              textAlign: 'center',
              background: 'rgba(255,255,255,0.9)',
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
            }}
          >
            <PlayCircleOutlined style={{ fontSize: '3rem', color: '#f5576c' }} />
            <Title level={3} style={{ marginTop: '15px' }}>故事剧场</Title>
            <Text style={{ display: 'block', marginBottom: '20px' }}>
              全屏播放动态童话，支持触摸互动
            </Text>
            <Button 
              type="primary" 
              size="large"
              style={{ 
                background: '#f5576c',
                borderColor: '#f5576c'
              }}
            >
              开始播放
            </Button>
          </Card>
        </div>

        {/* 上传区域 */}
        <Card style={{ 
          borderRadius: '15px',
          background: 'rgba(255,255,255,0.9)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
          textAlign: 'center'
        }}>
          <Upload.Dragger 
            name="image" 
            multiple={false}
            showUploadList={false}
            style={{ 
              background: 'rgba(102, 126, 234, 0.1)',
              borderColor: '#667eea'
            }}
          >
            <p className="ant-upload-drag-icon">
              <CloudUploadOutlined style={{ color: '#667eea' }} />
            </p>
            <p className="ant-upload-text" style={{ fontSize: '1.2rem' }}>
              点击或拖拽上传画作
            </p>
            <p className="ant-upload-hint">
              支持 JPG、PNG 格式，让您的画作动起来！
            </p>
          </Upload.Dragger>
          
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            gap: '20px', 
            marginTop: '20px',
            flexWrap: 'wrap'
          }}>
            <Button size="large" icon={<SoundOutlined />}>
              配音录制
            </Button>
            <Button size="large" icon={<ShareAltOutlined />}>
              分享作品
            </Button>
          </div>
        </Card>

        {/* 作品画廊预览 */}
        <div style={{ marginTop: '40px' }}>
          <Title level={2} style={{ color: 'white', textAlign: 'center' }}>
            创作作品展示
          </Title>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', 
            gap: '15px',
            marginTop: '20px'
          }}>
            {[1, 2, 3, 4].map(i => (
              <Card 
                key={i}
                cover={
                  <div style={{ 
                    height: '150px', 
                    background: `linear-gradient(45deg, #${Math.floor(Math.random()*16777215).toString(16)}, #${Math.floor(Math.random()*16777215).toString(16)})`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '3rem'
                  }}>
                    🎨
                  </div>
                }
                style={{ borderRadius: '10px' }}
              >
                <Card.Meta 
                  title={`作品 ${i}`} 
                  description="点击查看详情" 
                />
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* 扫描完成模态框 */}
      <Modal
        title="扫描完成"
        visible={isModalVisible}
        onOk={() => {
          setIsModalVisible(false);
          // 这里可以导航到编辑页面
        }}
        onCancel={handleCancel}
        okText="开始编辑"
        cancelText="稍后处理"
      >
        <p>您的画作已成功识别！</p>
        <p>检测到以下元素：</p>
        <ul>
          <li>人物角色：2个</li>
          <li>背景场景：1个</li>
          <li>装饰元素：5个</li>
        </ul>
        <p>现在可以为这些元素添加动画和故事了！</p>
      </Modal>
    </div>
  );
};

export default MagicCanvasHomePage;