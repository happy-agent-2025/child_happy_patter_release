import React from 'react'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import './App.css'

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <div className="App">
        <header className="App-header">
          <h1>Happy Partner - 儿童教育AI系统</h1>
          <p>前端界面开发中...</p>
        </header>
      </div>
    </ConfigProvider>
  )
}

export default App