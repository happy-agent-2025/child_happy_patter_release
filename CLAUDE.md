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

## 开发命令

**运行应用程序：**
```bash
python main.py
```

**运行所有测试：**
```bash
python -m pytest
```

**运行特定测试文件：**
```bash
python -m pytest tests/test_xxx.py
```

**运行详细测试输出：**
```bash
python -m pytest -v
```

**初始化数据库：**
```bash
python db/init_db.py
```

## 架构

- **API层**：FastAPI路由在 `api/routes.py`
- **数据库**：SQLAlchemy模型在 `db/` 目录，包含对话归档功能
- **代理**：模块化AI代理在 `agents/` 目录
- **服务**：音频处理服务在 `services/` 目录
- **测试**：全面的测试套件在 `tests/` 目录

## 主要功能

- 用户和代理类型级别的对话存储
- 对话归档和压缩以优化数据库
- 多个具有专门功能的AI代理
- 带声纹验证的音频处理
- 具有全面测试的RESTful API

## 测试

项目使用pytest和pytest-asyncio进行异步测试。测试配置在 `pytest.ini` 和 `tests/conftest.py` 中。

## 数据库管理

对话存储具有压缩和归档功能：
- `archive_old_conversations()`：归档并压缩旧对话
- `delete_old_conversations()`：删除指定天数前的对话
- 使用zlib压缩进行存储优化