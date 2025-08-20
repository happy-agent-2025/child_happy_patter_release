# Happy Partner - 儿童教育AI系统

一个多代理架构的儿童教育AI系统，专注于教育辅助和情感陪伴，具有音频处理、安全过滤和SQLite数据库功能。

## 项目概述

这是一个基于多代理架构的儿童教育AI系统，旨在为儿童提供教育辅助和情感陪伴。系统采用模块化设计，具备可扩展性，并集成了语音识别和合成技术。

## MVP功能

1. **多代理架构**:
   - MetaAgent: 请求路由和意图识别
   - SafetyAgent: 内容安全过滤
   - EduAgent: 教育内容问答

2. **音频处理**:
   - STT服务: 语音转文本
   - TTS服务: 文本转语音

3. **数据管理**:
   - SQLite数据库
   - SQLAlchemy ORM

4. **安全认证**:
   - JWT令牌认证
   - Bcrypt密码加密

## 项目结构

```
happy_partner/
├── api/              # API路由
├── agents/           # 各类代理
├── auth/             # 认证模块
├── config/           # 配置文件
├── core/             # 核心模块
├── db/               # 数据库相关
├── models/           # 数据模型
├── schemas/          # 数据模式
├── services/         # 服务模块
├── tests/            # 测试文件
├── utils/            # 工具模块
├── main.py           # 主应用文件
└── pytest.ini        # 测试配置
```

## 安装与运行

1. 安装依赖:
   ```bash
   pip install poetry
   poetry install
   ```

2. 运行应用:
   ```bash
   poetry run python main.py
   ```

3. 运行测试:
   ```bash
   poetry run pytest
   ```

## 开发计划

参考 [开发计划.md](../开发计划.md) 文件了解完整开发计划。

## API接口

- `POST /chat` - 主要聊天接口
- `POST /safety/check` - 内容安全检查接口
- `POST /edu/ask` - 教育问答接口

## 许可证

本项目仅供学习和参考使用。