# Happy Partner - 儿童教育AI系统

Happy Partner是一个专为儿童设计的教育AI系统，结合了多种AI代理来提供安全、有趣和个性化的学习体验。

## 系统架构

本系统采用模块化设计，主要包括以下组件：

- **Meta Agent**: 负责请求路由和分发
- **Safety Agent**: 内容安全检查，确保儿童接触的内容安全
- **Edu Agent**: 教育问答，提供学科知识解答
- **Memory Agent**: 对话记忆和上下文管理
- **Emotion Agent**: 情感陪伴，提供情绪支持
- **API服务**: FastAPI构建的RESTful API接口
- **数据库服务**: SQLAlchemy构建的数据持久化层

## 对话存储机制

系统采用用户和代理类型级对话存储机制，确保对话历史的完整性和可追溯性：

### 1. 用户和代理类型级存储
- 同一用户与同一代理类型的所有对话都存储在同一个数据库记录中
- 每次用户输入和AI响应都会追加到该记录中
- 通过user_id和agent_type关联同一用户与同一代理类型的对话

### 2. 对话历史结构
- 使用JSON格式存储完整的对话历史
- 每条对话包含用户输入、AI响应和时间戳
- 支持按时间顺序查询和检索对话历史

### 3. 对话历史查询接口
- `GET /users/{user_id}/conversations` - 获取用户对话历史
- `GET /users/{user_id}/conversations/recent` - 获取用户最近的对话记录
- `GET /users/{user_id}/conversations/{agent_type}` - 根据用户ID和代理类型获取对话记录
- `GET /sessions/{session_id}/conversations` - 获取会话中的所有对话

## 数据库优化建议

由于系统设计要求每次对话都创建新记录，长期运行会产生大量数据。为优化数据库性能和资源使用，建议采取以下措施：

### 4. 定期归档策略
- 将超过一定时间的历史数据移动到归档表中
- 保持主表数据量在合理范围内

### 5. 数据清理机制
- 定期删除不再需要的记录
- 根据业务需求设定数据保留期限

### 3. 表分区
- 按时间维度对对话表进行分区
- 提高查询性能，便于数据管理

### 4. 压缩存储
- 对历史数据采用压缩算法存储
- 减少磁盘空间占用

### 5. 索引优化
- 确保常用查询字段有适当索引
- 定期分析和优化索引使用情况

## 数据库优化功能

系统已实现以下数据库优化功能：

### 1. 对话记录归档
- [archive_old_conversations](file:///D:/rag/happy_partter/happy_partner/db/database_service.py#L302-L344)方法可将指定天数之前的对话记录归档并压缩存储
- 归档的数据会被移动到专门的归档表中，并在主表中删除
- 数据在归档过程中会使用zlib算法进行压缩以节省存储空间
- 归档表使用二进制字段存储压缩后的数据

### 2. 对话记录清理
- [delete_old_conversations](file:///D:/rag/happy_partter/happy_partner/db/database_service.py#L346-L367)方法可删除指定天数之前的对话记录
- 默认删除365天之前的记录，可以通过参数自定义

这些功能可以帮助管理系统长期运行产生的大量数据，保持数据库性能。

## 安装和运行

1. 克隆项目代码
2. 安装依赖: `poetry install`
3. 配置环境变量
4. 初始化数据库: `python db/init_db.py`
5. 启动服务: `python main.py`

## 测试

运行所有测试: `python -m pytest`

运行特定测试: `python -m pytest tests/test_xxx.py`

## 开发计划

参考 [开发计划.md](../开发计划.md) 文件了解完整开发计划。

## API接口

系统提供丰富的RESTful API接口，支持以下功能：

### 1. 对话交互接口
- `POST /chat` - 主要聊天接口
- `POST /safety/check` - 内容安全检查接口
- `POST /edu/ask` - 教育问答接口
- `POST /emotion/support` - 情感支持接口
- `POST /memory/manage` - 记忆管理接口

### 2. 用户和会话管理接口
- `POST /users/{user_id}/sessions` - 创建新会话
- `GET /users/{user_id}/sessions` - 获取用户的所有活跃会话
- `DELETE /sessions/{session_id}` - 删除会话（标记为非活跃）

## 许可证

本项目仅供学习和参考使用。