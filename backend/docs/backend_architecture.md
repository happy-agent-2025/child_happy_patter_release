# Backend 代码架构文档

## 项目概览

Happy Partner 儿童教育AI系统 - 基于 FastAPI 和 LangGraph 的多代理架构后端服务

## 技术栈

### 核心框架

- **FastAPI** (0.104.1) - Web 框架
- **LangGraph** (0.2.0) - 多代理状态图系统
- **LangChain** (0.2.0) - AI 应用开发框架
- **SQLAlchemy** (2.0.43) - ORM 数据库操作

### AI 与机器学习

- **OpenAI** (1.99.9) - GPT 模型接口
- **Transformers** (4.46.0) - Hugging Face 模型
- **Torch** (2.6.0) - 深度学习框架
- **Mem0AI** - 持久化记忆系统
- **Ollama** (0.4.7) - 本地模型服务

### 音频处理

- **Whisper** - 语音识别
- **Edge-TTS** - 文本转语音
- **LibROSA** - 音频分析
- **ChatTTS** - 对话式TTS

### 数据处理

- **Pydantic** - 数据验证
- **Pandas** - 数据分析
- **NumPy** - 数值计算

## 系统架构图

```mermaid
graph TB
    subgraph "API Layer"
        A[FastAPI Application]
        B[LangGraph Routes]
        C[Legacy Routes]
    end

    subgraph "Core Components"
        D[Multi-Agent System]
        E[Exception Handlers]
        F[CORS Middleware]
    end

    subgraph "AI Agents"
        G[Intent Agent]
        H[Safety Agent]
        I[Emotion Agent]
        J[Edu Agent]
        K[Memory Agent]
        L[World Agent]
        M[Role Factory]
        N[Role Agent]
        O[Chapter Manager]
    end

    subgraph "Data Layer"
        P[SQLAlchemy ORM]
        Q[Database Service]
        R[Models]
    end

    subgraph "External Services"
        S[OpenAI API]
        T[Ollama API]
        U[Audio Services]
    end

    subgraph "Memory System"
        V[Mem0 Memory Manager]
        W[Session Storage]
    end

    A --> B
    A --> C
    A --> E
    A --> F

    B --> D
    D --> G
    D --> H
    D --> I
    D --> J
    D --> K
    D --> L
    D --> M
    D --> N
    D --> O

    D --> P
    P --> Q
    Q --> R

    D --> V
    V --> W

    D --> S
    D --> T
    D --> U
```

# 目录结构

```mermaid
graph LR
    subgraph "Backend Root"
        A[main.py]
        B[requirements.txt]
        C[pytest.ini]
    end

    subgraph "Core Modules"
        D[agents/]
        E[api/]
        F[db/]
        G[models/]
        H[schemas/]
    end

    subgraph "Services"
        I[services/]
        J[utils/]
        K[memory/]
    end

    subgraph "Configuration"
        L[config/]
        M[core/]
        N[auth/]
    end

    subgraph "Testing"
        O[tests/]
        P[test_*.py files]
    end
```

## 核心模块详解

### 1. Agents 模块 (agents/)

```mermaid
graph TB
    subgraph "Multi-Agent System"
        A[multi_agent.py<br/>核心协调器]
        B[intent Agent<br/>意图识别]
        C[Safety Agent<br/>安全检查]
        D[Emotion Agent<br/>情感分析]
        E[Edu Agent<br/>教育问答]
        F[Memory Agent<br/>记忆管理]
        G[World Agent<br/>世界观生成]
        H[Role Factory<br/>角色创建]
        I[Role Agent<br/>角色扮演]
        J[Chapter Manager<br/>章节管理]
        K[LangGraph Workflow<br/>增强工作流]
        L[Meta Agent<br/>基础路由]
    end

    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    A --> H
    A --> I
    A --> J

    H --> I
    G --> H
    B --> H
    B --> G
```

### 2. API 模块 (api/)

```mermaid
graph LR
    subgraph "API Endpoints"
        A[langgraph_routes.py<br/>8个核心API端点]
        B[routes.py<br/>传统API端点]
    end

    subgraph "LangGraph Endpoints"
        C[/api/langgraph/chat<br/>聊天接口]
        D[/api/langgraph/chat/stream<br/>流式聊天]
        E[/api/langgraph/workflow/state<br/>工作流状态]
        F[/api/langgraph/analytics<br/>对话分析]
        G[/api/langgraph/session<br/>会话管理]
        H[/api/langgraph/test<br/>系统测试]
    end

    A --> C
    A --> D
    A --> E
    A --> F
    A --> G
    A --> H
```

### 3. 数据库模块 (db/)

```mermaid
graph TB
    subgraph "Database Layer"
        A[database.py<br/>连接配置]
        B[database_service.py<br/>服务层]
        C[init_db.py<br/>初始化]
    end

    subgraph "Models"
        D[User Model]
        E[Session Model]
        F[Conversation Model]
        G[Voiceprint Model]
    end

    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
```

### 4. 服务模块 (services/)

```mermaid
graph LR
    subgraph "AI Services"
        A[OpenAI Client]
        B[Ollama Client]
        C[STT Service<br/>语音识别]
        D[TTS Service<br/>语音合成]
        E[Audio Processing]
    end

    subgraph "External APIs"
        F[Dashscope]
        G[ModelScope]
        H[Fish Speech]
    end

    A --> F
    B --> G
    C --> H
    D --> H
```

## 数据流程图

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant MA as Multi-Agent
    participant IA as Intent Agent
    participant SA as Safety Agent
    participant AA as AI Service
    participant DB as Database

    U->>API: 发送消息
    API->>MA: 处理请求
    MA->>IA: 意图识别
    IA->>MA: 返回意图类型

    alt 聊天模式
        MA->>SA: 安全检查
        SA->>MA: 安全验证结果
        MA->>AA: 生成回复
        AA->>MA: 返回AI回复
    else 故事模式
        MA->>G: 创建世界观
        MA->>H: 创建角色
        MA->>AA: 生成故事内容
        AA->>MA: 返回故事
    end

    MA->>DB: 存储对话记录
    DB->>MA: 确认存储
    MA->>API: 返回响应
    API->>U: 返回结果
```

## 多代理工作流

```mermaid
stateDiagram-v2
    [*] --> Input_Processor

    Input_Processor --> Intent_Router: 接收用户输入
    Intent_Router --> Safety_Checker: 意图识别

    Safety_Checker --> Chat_Handler: 聊天模式
    Safety_Checker --> Story_World_Builder: 故事模式

    Chat_Handler --> Emotion_Analyzer: 情感分析
    Emotion_Analyzer --> Memory_Updater: 记忆更新
    Memory_Updater --> Response_Formatter: 格式化响应

    Story_World_Builder --> Story_Role_Manager: 角色管理
    Story_Role_Manager --> Story_Interactive: 故事互动
    Story_Interactive --> Chapter_Manager: 章节管理
    Chapter_Manager --> Response_Formatter

    Response_Formatter --> Voice_Output_Processor: 语音处理
    Voice_Output_Processor --> [*]
```

## 配置管理

```mermaid
graph TB
    subgraph "Configuration"
        A[settings.py<br/>应用配置]
        B[Environment Variables<br/>环境变量]
        C[Database Config<br/>数据库配置]
    end

    subgraph "Security"
        D[JWT Settings<br/>JWT配置]
        E[CORS Settings<br/>跨域配置]
        F[Auth Utils<br/>认证工具]
    end

    A --> B
    A --> C
    B --> D
    B --> E
    B --> F
```

## 错误处理架构

```mermaid
graph LR
    subgraph "Exception Handling"
        A[Core Exceptions]
        B[HTTP Exceptions]
        C[Validation Errors]
    end

    subgraph "Error Handlers"
        D[Global Handler]
        E[API Handler]
        F[Database Handler]
    end

    A --> D
    B --> E
    C --> F
    D --> A
    E --> B
    F --> C
```

## 测试架构

```mermaid
graph TB
    subgraph "Test Suite"
        A[Unit Tests<br/>单元测试]
        B[Integration Tests<br/>集成测试]
        C[API Tests<br/>API测试]
        D[Real Interface Tests<br/>真实接口测试]
    end

    subgraph "Test Tools"
        E[Pytest<br/>测试框架]
        F[Test Client<br/>测试客户端]
        G[Mock Objects<br/>模拟对象]
        H[Database Fixtures<br/>数据库夹具]
    end

    A --> E
    B --> E
    C --> E
    D --> E

    A --> F
    B --> G
    C --> F
    D --> F

    All --> H
```

## 部署架构

```mermaid
graph TB
    subgraph "Production"
        A[Uvicorn Server<br/>ASGI服务器]
        B[FastAPI App<br/>应用实例]
        C[Database<br/>SQLite/PostgreSQL]
    end

    subgraph "Development"
        D[Local Server<br/>本地开发]
        E[Test Database<br/>测试数据库]
        F[Mock Services<br/>模拟服务]
    end

    subgraph "External Services"
        G[OpenAI API<br/>AI服务]
        H[Ollama Service<br/>本地AI]
        I[Audio Services<br/>音频服务]
    end

    A --> B
    B --> C
    B --> G
    B --> H
    B --> I
```

## 代码质量指标

- **总文件数**: 87个Python文件
- **代码行数**: 约8,000+行
- **测试覆盖率**: 16-20%
- **模块化程度**: 高度模块化设计
- **文档覆盖**: 完整的API文档和代码注释

## 性能特点

- **异步处理**: 基于FastAPI的异步架构
- **多代理并行**: LangGraph状态图支持并行处理
- **缓存机制**: 记忆系统和会话缓存
- **数据库优化**: SQLAlchemy ORM优化查询
- **API响应**: 平均响应时间2-10秒

## 安全特性

- **内容安全**: SafetyAgent进行内容过滤
- **输入验证**: Pydantic数据验证
- **认证机制**: JWT token认证
- **CORS配置**: 跨域安全配置
- **异常处理**: 全局异常捕获机制
