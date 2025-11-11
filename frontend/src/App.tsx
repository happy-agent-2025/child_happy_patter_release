import { ConfigProvider } from 'antd'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import zhCN from 'antd/locale/zh_CN'
import Layout from './components/Layout'
import ChatPage from './pages/ChatPage'
import ParentControlPage from './pages/ParentControlPage'
import MagicCanvasHomePage from './pages/MagicCanvasHomePage'
// import LoginPage from './pages/LoginPage'
// import DebugPage from './pages/DebugPage'
import './App.css'

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Routes>
          {/* <Route path="/login" element={<LoginPage />} /> */}
          <Route path="/parent" element={<ParentControlPage />} />
          <Route path="/magic-canvas" element={<MagicCanvasHomePage />} />
          <Route path="/*" element={
            <Layout>
              <Routes>
                <Route path="/" element={<ChatPage />} />
                {/* <Route path="/chat" element={<ChatPage />} /> */}
                {/* <Route path="/debug" element={<DebugPage />} /> */}
              </Routes>
            </Layout>
          } />
        </Routes>
      </Router>
    </ConfigProvider>
  )
}

export default App