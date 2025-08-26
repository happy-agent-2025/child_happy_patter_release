import React from 'react'
import { ConfigProvider } from 'antd'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import zhCN from 'antd/locale/zh_CN'
import Layout from './components/Layout'
import ChatPage from './pages/ChatPage'
import LoginPage from './pages/LoginPage'
import './App.css'

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/*" element={
            <Layout>
              <Routes>
                <Route path="/" element={<ChatPage />} />
                <Route path="/chat" element={<ChatPage />} />
              </Routes>
            </Layout>
          } />
        </Routes>
      </Router>
    </ConfigProvider>
  )
}

export default App