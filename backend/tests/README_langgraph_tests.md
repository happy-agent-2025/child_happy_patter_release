# LangGraph Routes API 测试文档

## 概述

本文档描述了 `test_langgraph_routes_comprehensive.py` 测试套件，该套件提供了对 `langgraph_routes.py` 中所有8个API端点的全面测试覆盖。

## 测试覆盖范围

### API端点覆盖

| 端点 | 方法 | 描述 | 测试类 |
|------|------|------|--------|
| `/langgraph/chat` | POST | 主要聊天接口 | `TestLangGraphChat` |
| `/langgraph/chat/stream` | POST | 流式聊天接口 | `TestLangGraphStreamChat` |
| `/langgraph/workflow/state` | GET | 工作流状态查询 | `TestWorkflowState` |
| `/langgraph/analytics/conversation-flow` | GET | 对话流分析 | `TestConversationFlowAnalytics` |
| `/langgraph/session/create` | POST | 创建会话 | `TestSessionCreate` |
| `/langgraph/session/{session_id}/history` | GET | 获取会话历史 | `TestSessionHistory` |
| `/langgraph/users/{user_id}/insights` | GET | 用户行为洞察 | `TestUserInsights` |
| `/langgraph/test/workflow` | POST | 工作流测试接口 | `TestWorkflowTest` |

### 测试类型覆盖

1. **功能测试** - 验证每个API端点的正常功能
2. **参数验证测试** - 测试各种参数组合和验证规则
3. **错误处理测试** - 测试异常情况和错误响应
4. **边界条件测试** - 测试极端值和边界情况
5. **集成测试** - 测试多步骤的工作流程
6. **性能测试** - 测试响应时间和并发处理
7. **Unicode和国际化测试** - 测试多语言内容处理

## 运行测试

### 方法1: 使用便捷脚本

```bash
# 运行所有测试
python run_langgraph_tests.py

# 详细输出
python run_langgraph_tests.py --verbose

# 只运行特定测试类
python run_langgraph_tests.py --class TestLangGraphChat

# 生成覆盖率报告
python run_langgraph_tests.py --coverage

# 跳过慢速测试
python run_langgraph_tests.py --markers "not slow"

# 列出所有测试
python run_langgraph_tests.py --list-tests
```

### 方法2: 直接使用pytest

```bash
# 运行所有测试
pytest tests/test_langgraph_routes_comprehensive.py -v

# 运行特定测试类
pytest tests/test_langgraph_routes_comprehensive.py::TestLangGraphChat -v

# 运行特定测试方法
pytest tests/test_langgraph_routes_comprehensive.py::TestLangGraphChat::test_chat_success -v

# 生成覆盖率报告
pytest tests/test_langgraph_routes_comprehensive.py --cov=api.langgraph_routes --cov-report=html

# 只运行失败的测试
pytest tests/test_langgraph_routes_comprehensive.py -lf
```

## 测试环境设置

### 依赖要求

```bash
pip install pytest pytest-asyncio pytest-cov fastapi testclient sqlalchemy
```

### 环境变量

测试使用内存SQLite数据库，无需额外的数据库配置。如果需要测试其他数据库，可以设置环境变量：

```bash
export DATABASE_URL="sqlite:///:memory:"
export OPENAI_API_KEY="your_test_key"  # 用于模拟测试
```

## 测试数据说明

### Mock对象

测试使用了以下Mock对象：

1. **MockMultiAgent** - 模拟多代理系统
   - `process_message()` - 模拟消息处理
   - `get_system_statistics()` - 模拟系统统计

2. **测试数据库** - 使用内存SQLite
   - 自动创建和销毁测试数据
   - 独立的测试用户、会话和对话记录

### 测试数据结构

- **测试用户**: ID=1, username="testuser"
- **测试会话**: ID=1, title="测试会话"
- **测试对话**: 5条不同时间的对话记录

## 测试用例详解

### TestLangGraphChat (聊天接口测试)

```python
# 正常聊天测试
def test_chat_success(self, test_user)

# 带会话ID的聊天
def test_chat_with_session(self, test_user, test_session)

# 缺少必需字段
def test_chat_missing_content(self)

# 异常处理
def test_chat_with_exception(self, mock_agent, mock_db_service)
```

### TestConversationFlowAnalytics (对话流分析测试)

```python
# 正常分析
def test_conversation_flow_success(self, test_user, test_conversations)

# 无对话记录
def test_conversation_flow_no_conversations(self, test_user)

# 参数验证
def test_conversation_flow_invalid_days(self, test_user)

# 缺少参数
def test_conversation_flow_missing_user_id(self)
```

### TestIntegration (集成测试)

```python
# 完整聊天流程
def test_complete_chat_flow(self, test_user)

# 并发请求处理
def test_concurrent_requests(self, test_user)
```

## 性能基准

### 响应时间要求

- **正常API调用**: < 5秒
- **简单查询**: < 1秒
- **数据分析**: < 3秒

### 并发测试

- 支持5个并发请求同时处理
- 无死锁或竞态条件

## 覆盖率目标

- **行覆盖率**: > 90%
- **分支覆盖率**: > 85%
- **函数覆盖率**: 100%

## 故障排除

### 常见问题

1. **ImportError**: 确保所有依赖已安装
2. **Database errors**: 检查数据库连接配置
3. **Async errors**: 确保pytest-asyncio已安装
4. **Mock failures**: 检查patch路径是否正确

### 调试技巧

```bash
# 运行单个测试并显示详细输出
pytest tests/test_langgraph_routes_comprehensive.py::TestLangGraphChat::test_chat_success -v -s

# 在测试中添加断点
import pdb; pdb.set_trace()

# 查看测试输出
pytest tests/test_langgraph_routes_comprehensive.py -v -s --tb=long
```

## 扩展测试

### 添加新测试

1. 在相应的测试类中添加新方法
2. 方法名以 `test_` 开头
3. 使用适当的fixture和Mock对象

### 添加新端点测试

1. 创建新的测试类
2. 继承基本测试模式
3. 包含成功和失败场景

### 性能测试扩展

```python
def test_specific_performance_scenario(self):
    """测试特定性能场景"""
    # 实现具体的性能测试逻辑
    pass
```

## 最佳实践

1. **测试隔离**: 每个测试应该独立运行
2. **数据清理**: 使用fixture自动清理测试数据
3. **Mock使用**: 合理使用Mock避免外部依赖
4. **断言完整**: 验证所有重要的响应字段
5. **错误覆盖**: 测试所有可能的错误路径

## 报告和监控

### 覆盖率报告

运行 `python run_langgraph_tests.py --coverage` 后查看：

- `htmlcov/index.html` - 详细的HTML覆盖率报告
- 终端输出 - 简要的覆盖率统计

### 持续集成

建议在CI/CD流水线中包含这些测试：

```yaml
- name: Run LangGraph API Tests
  run: |
    python run_langgraph_tests.py --coverage
    # 上传覆盖率报告到代码质量工具
```

## 维护指南

- 定期更新Mock对象以匹配实际API变更
- 添加新功能时同步添加相应测试
- 定期检查测试覆盖率并补充缺失的测试
- 监控测试执行时间，优化慢速测试