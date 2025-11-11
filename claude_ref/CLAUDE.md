# CLAUDE.md

本文件为Claude Code (claude.ai/code) 提供在此代码库中工作的指导。

## 项目概述

Happy Partner是一个多代理教育AI系统，专为儿童设计，使用FastAPI和SQLAlchemy构建。系统包含：
- Meta Agent：请求路由和分发
- Safety Agent：内容安全检查
- Edu Agent：教育问答
- Memory Agent：对话记忆管理
- Emotion Agent：情感支持
- 音频服务：语音转文本、文本转语音、声纹验证

### 开发计划目录
./开发计划.md

## 开发命令

### 后端开发命令

**运行应用程序：**
```bash
cd backend
python main.py
```

**运行所有测试：**
```bash
cd backend
python -m pytest
```

**运行带覆盖率测试：**
```bash
cd backend
python -m pytest --cov=. --cov-report=term-missing
```

**运行特定测试文件：**
```bash
cd backend
python -m pytest tests/test_xxx.py
```

**运行详细测试输出：**
```bash
cd backend
python -m pytest -v
```

**初始化数据库：**
```bash
cd backend
python db/init_db.py
```

**查看API文档：**
```bash
cd backend
python main.py
# 然后访问 http://localhost:8000/docs
```

### 前端开发命令

**安装依赖：**
```bash
cd frontend
npm install
```

**开发模式运行：**
```bash
cd frontend
npm run dev
```

**生产构建：**
```bash
cd frontend
npm run build
```

**代码检查：**
```bash
cd frontend
npm run lint
```

**预览生产构建：**
```bash
cd frontend
npm run preview
```

## 架构

### 后端架构
- **API层**：FastAPI路由在 `api/routes.py`
- **数据库**：SQLAlchemy模型在 `db/` 目录，包含对话归档功能
- **代理**：模块化AI代理在 `agents/` 目录
- **服务**：音频处理服务在 `services/` 目录
- **测试**：全面的测试套件在 `tests/` 目录
- **认证**：JWT认证系统在 `auth/` 目录
- **配置**：应用配置在 `config/` 目录
- **模型**：数据模型在 `models/` 目录
- **Schema**：Pydantic模型在 `schemas/` 目录

### 前端架构
- **技术栈**：React 18 + TypeScript 5 + Vite 5 + Ant Design 5
- **组件**：可复用组件在 `frontend/src/components/`
- **页面**：页面组件在 `frontend/src/pages/`
- **服务**：API服务层在 `frontend/src/services/`
- **状态管理**：Redux Toolkit + React Query
- **路由**：React Router v7 路由系统

### 核心模块
- **Meta Agent** (`agents/meta_agent.py`)：智能请求路由和分发
- **Safety Agent** (`agents/safety_agent.py`)：内容安全审查
- **Edu Agent** (`agents/edu_agent.py`)：教育问答
- **Emotion Agent** (`agents/emotion_agent.py`)：情感陪伴
- **Memory Agent** (`agents/memory_agent.py`)：对话记忆管理
- **音频服务** (`services/` 目录)：STT、TTS、声纹验证
- **数据库服务** (`db/database_service.py`)：对话存储和归档

## 主要功能

- 用户和代理类型级别的对话存储
- 对话归档和压缩以优化数据库
- 多个具有专门功能的AI代理
- 带声纹验证的音频处理
- 具有全面测试的RESTful API
- 现代化前端界面

## 技术栈版本

**后端：**
- Python 3.13.5
- FastAPI 0.68.2
- SQLAlchemy 2.0.43
- Pydantic 1.10.22
- Pytest 8.4.1

**前端：**
- React 18.2.0
- TypeScript 5.2.2
- Vite 5.0.0
- Ant Design 5.12.8
- Redux Toolkit 1.9.7
- React Query 5.13.1

## 测试

项目使用pytest和pytest-asyncio进行异步测试。测试配置在 `pytest.ini` 和 `tests/conftest.py` 中。

## 数据库管理

对话存储具有压缩和归档功能：
- `archive_old_conversations()`：归档并压缩旧对话
- `delete_old_conversations()`：删除指定天数前的对话
- 使用zlib压缩进行存储优化
- 始终以中文回答
- 提交代码时，提交信息必须中文填写