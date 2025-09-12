import { Component, ErrorInfo, ReactNode } from 'react';
import { Result, Button } from 'antd';

// 声明 process 全局变量，解决类型错误
declare global {
  interface Window {
    process: {
      env: {
        NODE_ENV: string;
      };
    };
  }
}

// 确保 process 可用
const nodeEnv = typeof process !== 'undefined' 
  ? process.env.NODE_ENV 
  : (window.process?.env?.NODE_ENV || 'production');

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Result
          status="error"
          title="出现了一些问题"
          subTitle="应用遇到了意外错误，请尝试刷新页面或联系技术支持。"
          extra={[
            <Button type="primary" key="retry" onClick={this.handleReset}>
              重试
            </Button>,
            <Button key="refresh" onClick={() => window.location.reload()}>
              刷新页面
            </Button>
          ]}
        >
          {nodeEnv === 'development' && (
            <div style={{ textAlign: 'left', marginTop: 16 }}>
              <details style={{ whiteSpace: 'pre-wrap' }}>
                <summary>错误详情 (开发模式)</summary>
                <p><strong>错误信息:</strong> {this.state.error?.message}</p>
                <p><strong>错误堆栈:</strong></p>
                <pre>{this.state.error?.stack}</pre>
                <p><strong>组件堆栈:</strong></p>
                <pre>{this.state.errorInfo?.componentStack}</pre>
              </details>
            </div>
          )}
        </Result>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;