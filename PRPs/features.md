name: "面向儿童教育的多智能体AI对话系统实现"
description: |

## Purpose
实现一个专为儿童教育设计的复杂多智能体AI对话系统，具有简单聊天和故事模式两种交互方式，集成语音处理、情感智能、安全合规和动态故事生成功能。

## Core Principles
1. **儿童安全优先**: 所有内容必须适合儿童，包含多层安全检查
2. **教育价值导向**: 系统应具有教育意义，促进儿童学习和成长
3. **交互友好性**: 针对儿童用户特点设计简单直观的交互方式
4. **多模态支持**: 支持语音、文字等多种交互方式
5. **Global rules**: 必须遵循CLAUDE.md中的所有规则

---

## Goal
实现一个完整的多智能体AI对话系统，能够：
1. 智能识别用户意图并路由到相应功能模块
2. 提供简单聊天模式，包含情感智能和安全检查
3. 提供故事模式，支持动态故事创作和角色扮演
4. 集成语音处理功能，支持语音输入输出
5. 使用mem0持久化记忆系统维护对话连续性

## Why
- **儿童教育市场需求**: 随着AI技术发展，儿童教育领域需要智能化、互动性强的学习工具
- **现有系统不足**: 当前儿童AI助手往往功能单一，缺乏系统性设计
- **技术整合需求**: 需要整合多种AI技术（语音识别、自然语言处理、情感分析）提供完整体验
- **安全性考虑**: 儿童产品对内容安全和隐私保护有极高要求

## What
实现一个模块化的多智能体系统，包含以下核心功能：

### 系统架构
1. **前端处理层**: 语音输入处理、语音转文字(STT)、文字转语音(TTS)
2. **智能路由层**: 意图识别智能体，根据用户内容路由到相应功能模块
3. **功能处理层**:
   - 简单聊天模式：情感智能体 + 安全审查智能体
   - 故事模式：世界观智能体 + 角色智能体群组
4. **记忆管理层**: 基于mem0的持久化记忆系统
5. **输出处理层**: TTS转换和音频输出

### 技术要求
- 使用FastAPI构建后端API
- 使用React + TypeScript构建前端界面
- 集成多种AI模型（OpenAI、Ollama、vLLM）
- 实现mem0记忆管理系统
- 支持实时语音处理

### Success Criteria
- [ ] 意图识别准确率达到90%以上
- [ ] 故事创作能够生成连贯、有趣、适合儿童的内容
- [ ] 语音处理延迟控制在2秒以内
- [ ] 安全检查能够过滤99%以上的不适宜内容
- [ ] 系统能够支持100个并发用户
- [ ] 记忆系统能够准确维护对话上下文

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://docs.mem0.ai
  why: mem0记忆管理系统的核心文档，用于实现持久化记忆功能

- url: https://fastapi.tiangolo.com
  why: FastAPI框架文档，用于构建后端API服务

- url: https://langchain-ai.github.io/langgraph/
  why: LangGraph文档，用于构建多智能体工作流

- file: backend/agents/story_graph.py
  why: 现有故事创作系统的实现模式，包含LangGraph工作流和mem0集成

- file: backend/agents/meta_agent.py
  why: 现有元代理的实现模式，展示如何进行智能路由

- file: claude_ref/INITIAL.md
  why: 功能需求文档，描述了系统的整体架构和功能特性

- file: backend/config/settings.py
  why: 配置管理模式，了解系统配置结构
```

### Current Codebase tree
```bash
.
├── backend/                 # 后端服务
│   ├── agents/             # 智能体模块
│   │   ├── meta_agent.py   # 元代理 - 意图识别和路由
│   │   ├── story_graph.py  # 故事创作系统（已实现LangGraph + mem0）
│   │   ├── safety_agent.py # 安全代理
│   │   ├── edu_agent.py    # 教育代理
│   │   ├── emotion_agent.py # 情感代理
│   │   └── memory_agent.py # 记忆代理
│   ├── api/                # API路由
│   ├── services/           # 语音处理服务
│   ├── config/             # 配置管理
│   ├── db/                 # 数据库层
│   └── utils/              # 工具函数
├── frontend/               # 前端React应用
└── PRPs/                   # 项目需求文档
```

### Desired Codebase tree with files to be added
```bash
.
├── backend/
│   ├── agents/
│   │   ├── intent_agent.py         # 意图识别智能体（新增）
│   │   ├── world_agent.py  # 世界观智能体（新增）
│   │   ├── role_agent.py      # 角色智能体（新增）
│   │   ├── role_factory.py        # 角色工厂（新增）
│   │   └── chapter_manager.py     # 章节管理中心（新增）
│   ├── services/
│   │   ├── stt_service.py          # 语音转文字服务（增强）
│   │   ├── tts_service.py          # 文字转语音服务（增强）
│   │   └── voice_verification.py   # 声纹验证（新增）
│   ├── memory/
│   │   └── mem0.py     # mem0集成模块（新增）
│   └── api/
│       └── story_routes.py        # 故事模式API路由（新增）
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── VoiceInput.tsx      # 语音输入组件（新增）
    │   │   ├── StoryMode.tsx       # 故事模式组件（新增）
    │   │   └── RoleSelect.tsx # 角色选择组件（新增）
    │   ├── services/
    │   │   └── storyApi.ts         # 故事API服务（新增）
    │   └── stores/
    │       └── storyStore.ts       # 故事状态管理（新增）
```

### Known Gotchas of our codebase & Library Quirks
```python
# CRITICAL: FastAPI路由需要使用async函数
# Example: @app.post("/chat") async def chat_endpoint(request: ChatRequest)

# CRITICAL: 系统已配置多种AI模型支持（OpenAI、Ollama、vLLM）
# 优先级：Ollama > vLLM > OpenAI，需要处理模型切换和降级

# CRITICAL: mem0配置需要Qdrant向量数据库
# 从story_graph.py可以看到mem0配置模式，需要确保Qdrant服务运行

# CRITICAL: 儿童内容安全要求极高
# 需要实施多层安全检查，包括输入验证、内容过滤、输出审查

# CRITICAL: 语音处理需要优化延迟
# 现有音频服务需要针对实时交互进行优化
```

## Implementation Blueprint

### Data models and structure

创建核心数据模型，确保类型安全和一致性：
```python
# 意图识别模型
class IntentRequest(BaseModel):
    content: str
    user_id: str
    session_id: Optional[str] = None

# 故事世界模型
class StoryWorld(BaseModel):
    world_name: str
    world_type: str
    background: str
    rules: str
    roles: List[str]
    themes: List[str]

# 角色配置模型
class RoleConfig(BaseModel):
    name: str
    personality: str
    background: str
    prompt_template: str
    voice_id: Optional[str] = None
```

### list of tasks to be completed to fullfill the PRP in the order they should be completed

```yaml
Task 1 - 意图识别智能体:
CREATE backend/agents/intent_agent.py:
  - 基于meta_agent.py的模式扩展
  - 添加专门的故事模式检测逻辑
  - 集成情感分析功能
  - 支持语音唤醒词识别

Task 2 - 世界观智能体:
CREATE backend/agents/world_agent.py:
  - 实现基于用户输入的世界观生成
  - 集成安全检查机制
  - 支持多种故事模板
  - 生成适合儿童的世界观设定

Task 3 - 角色工厂系统:
CREATE backend/agents/role_factory.py:
  - 实现动态智能体创建
  - 管理智能体生命周期
  - 处理并发和资源管理
  - 集成mem0记忆系统

Task 4 - 角色智能体实现:
CREATE backend/agents/role_agent.py:
  - 实现角色专用智能体
  - 支持个性化回应
  - 集成TTS声音定制
  - 保持角色一致性

Task 5 - 章节管理中心:
CREATE backend/agents/chapter_manager.py:
  - 实现故事章节管理
  - 协调多个角色智能体
  - 管理故事进度
  - 集成记忆存储

Task 6 - mem0集成:
CREATE backend/memory/mem0.py:
  - mem0集成
  - 实现世界观数据存储
  - 支持长期记忆管理
  - 优化检索性能

Task 7 - 语音服务:
MODIFY backend/services/:
  - 提升STT服务准确性
  - 优化TTS语音质量
  - 添加声纹验证功能
  - 降低处理延迟

Task 8 - API路由实现:
CREATE backend/api/story_routes.py:
  - 实现故事模式API
  - 添加WebSocket支持
  - 实现实时通信
  - 集成安全中间件

Task 9 - 前端组件实现:
CREATE frontend/src/components/:
  - 实现语音输入组件
  - 创建故事模式界面
  - 实现角色选择功能
  - 添加动画效果

Task 10 - 状态管理和服务:
CREATE frontend/src/stores/ and frontend/src/services/:
  - 实现故事状态管理
  - 创建API服务层
  - 实现实时数据同步
  - 添加错误处理

Task 11 - 系统集成测试:
CREATE tests/integration/:
  - 端到端测试
  - 性能测试
  - 安全测试
  - 用户体验测试

Task 12 - 文档和部署:
CREATE docs/ and docker/:
  - 系统文档
  - 部署脚本
  - 监控配置
  - 性能优化
```

### Per task pseudocode as needed added to each task

```python
# Task 1 - 意图识别智能体
class IntentAgent(MetaAgent):
    def __init__(self):
        super().__init__()
        self.wakeup_words = ["贝贝你好", "小贝贝", "讲故事", "贝贝", "开始游戏"]

    def detect_intent(self, content: str, user_id: str) -> Dict[str, Any]:
        # PATTERN: 使用现有多模型调用模式
        prompt = f"""
        分析用户意图，支持以下模式：
        1. chat - 普通对话
        2. story - 故事创作

        用户输入: {content}
        用户ID: {user_id}
        """

        # GOTCHA: 使用多模型降级策略
        response = self._call_model_with_fallback(prompt)

        return {
            "intent": self._parse_intent(response),
            "confidence": self._calculate_confidence(response),
            "wakeup_detected": self._check_wakeup_words(content)
        }

# Task 2 - 世界观智能体
class WorldAgent:
    def create_world(self, user_description: str, user_id: str) -> StoryWorld:
        # PATTERN: 遵循现有安全检查模式
        safety_check = self._safety_agent.validate_content(user_description)
        if not safety_check.is_safe:
            raise SafetyException("内容不安全")

        # PATTERN: 使用模板和AI生成结合
        base_template = self._select_world_template(user_description)

        prompt = f"""
        基于用户描述创建儿童友好的故事世界：
        用户描述: {user_description}
        基础模板: {base_template}

        生成JSON格式的世界观设定
        """

        world_data = self._call_model_api(prompt)
        return self._parse_and_validate_world(world_data)

# Task 3 - 角色工厂
class RoleFactory:
    def __init__(self):
        self.active_roles = {}
        self.memory_client = self._init_memory_client()

    def create_role_agent(self, role_config: RoleConfig) -> Role:
        # PATTERN: 使用动态类创建模式
        role_class = type(
            f"Role_{role_config.name}",
            (BaseRole,),
            {
                "role_config": role_config,
                "memory_client": self.memory_client
            }
        )

        # GOTCHA: 处理线程安全和资源管理
        role = role_class()
        self.active_roles[role_config.name] = role

        return role

    def manage_role_lifecycle(self, role_id: str):
        # PATTERN: 实现资源清理和状态管理
        if role_id in self.active_roles:
            role = self.active_roles[role_id]
            self._cleanup_role_resources(role)
            del self.active_roles[role_id]
```

### Integration Points
```yaml
DATABASE:
  - migration: "Add tables for story_worlds, role_agents, sessions"
  - indexes: "CREATE INDEX idx_user_sessions ON sessions(user_id)"

CONFIG:
  - add to: backend/config/settings.py
  - patterns: |
      STORY_CONFIG = {
          "max_roles_per_story": 5,
          "max_chapters_per_story": 20,
          "safety_check_level": "strict"
      }

ROUTES:
  - add to: backend/main.py
  - pattern: "app.include_router(story_router, prefix='/api/v1/story')"

MEM0:
  - config: "Update mem0 config for story-specific collections"
  - migration: "Create dedicated story memory collections"

SERVICES:
  - external: "Qdrant vector database for mem0"
  - external: "Redis for session management"
  - external: "WebSocket server for real-time communication"
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
cd backend
python -m ruff check agents/ --fix  # Auto-fix what's possible
python -m mypy agents/              # Type checking

cd frontend
npm run lint                        # ESLint checking
npm run type-check                  # TypeScript checking

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests
```python
# CREATE tests/test_agents.py with these test cases:
def test_intent_agent_routing():
    """意图识别路由准确性测试"""
    agent = IntentAgent()

    # 测试故事创建意图
    result = agent.detect_intent("我想创建一个魔法世界", "user123")
    assert result["intent"] == "story_creation"
    assert result["confidence"] > 0.8

    # 测试角色扮演意图
    result = agent.detect_intent("我要扮演小魔法师", "user123")
    assert result["intent"] == "role_play"

def test_world_safety():
    """世界观安全检查测试"""
    builder = WorldAgent()

    # 测试不安全内容被拒绝
    with pytest.raises(SafetyException):
        builder.create_world("包含暴力内容", "user123")

    # 测试安全内容正常创建
    world = builder.create_world("美丽的魔法森林", "user123")
    assert world.world_name is not None

def test_role_factory_creation():
    """角色工厂创建测试"""
    factory = RoleFactory()
    role_config = RoleConfig(
        name="小魔法师",
        personality="勇敢而好奇",
        background="魔法学校的学生",
        prompt_template="魔法学生模板"
    )

    role = factory.create_role_agent(role_config)
    assert role.name == "小魔法师"
    assert len(factory.active_roles) == 1
```

```bash
# Run and iterate until passing:
cd backend
python -m pytest tests/test_agents.py -v
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test
```bash
# Start the backend service
cd backend
python main.py

# Test story creation endpoint
curl -X POST http://localhost:8000/api/v1/story/world \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "description": "我想创建一个太空冒险故事",
    "session_id": "session_123"
  }'

# Expected: {
#   "world_id": "world_123",
#   "world_name": "太空冒险",
#   "status": "created"
# }

# Test role creation
curl -X POST http://localhost:8000/api/v1/story/role \
  -H "Content-Type: application/json" \
  -d '{
    "world_id": "world_123",
    "role_name": "小宇航员",
    "personality": "勇敢探索",
    "user_id": "test_user"
  }'

# Test story interaction
curl -X POST http://localhost:8000/api/v1/story/interact \
  -H "Content-Type: application/json" \
  -d '{
    "world_id": "world_123",
    "role_id": "char_123",
    "message": "我们开始探索这个星球吧！",
    "user_id": "test_user"
  }'
```

## Final validation Checklist
- [ ] 所有智能体功能正常工作: `python -m pytest tests/agents/ -v`
- [ ] API路由全部通过测试: `python -m pytest tests/api/ -v`
- [ ] 语音处理延迟测试通过: `python tests/test_voice_latency.py`
- [ ] 安全检查测试100%通过: `python tests/test_safety.py`
- [ ] mem0记忆功能正常: `python tests/test_memory.py`
- [ ] 前端组件渲染正常: `npm run test`
- [ ] 端到端测试通过: `python tests/e2e/test_full_workflow.py`
- [ ] 性能测试达标: `python tests/test_performance.py`
- [ ] 用户验收测试通过

---

## Anti-Patterns to Avoid
- ❌ 不要创建复杂的继承层次，优先使用组合模式
- ❌ 不要忽略儿童安全检查，所有内容必须经过验证
- ❌ 不要使用同步I/O操作，所有网络调用必须是异步的
- ❌ 不要硬编码AI模型配置，使用配置文件管理
- ❌ 不要忽略错误处理，必须优雅处理所有异常情况
- ❌ 不要在前端实现业务逻辑，所有业务逻辑必须在后端
- ❌ 不要忽略内存使用，智能体需要适当的资源管理
- ❌ 不要忽略用户体验，儿童界面需要简单直观

## 质量评分: 9/10

这个PRP具有高度的可实现性，因为：
1. 模块化设计便于迭代开发
2. 明确的技术实现路径
3. 完整的验证和测试策略
4. 详细的安全和性能考虑 