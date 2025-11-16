# Happy Partner 配置系统指南

## 概述

Happy Partner 使用基于 Pydantic Settings 的统一配置系统，支持环境变量和 `.env` 文件配置。

## 配置文件结构

### 主要配置文件
- `config/settings.py` - 主配置类定义
- `.env` - 环境变量配置文件（可选）
- `.env.example` - 环境变量配置示例

## 配置类别

### 应用配置
```python
app_name: str = "Happy Partner - 儿童教育AI系统"
app_version: str = "0.2.0"
app_description: str = "一个多代理架构的儿童教育AI系统，专注于教育辅助和情感陪伴"
```

### 服务器配置
```python
host: str = "127.0.0.1"
port: int = 8001
debug: bool = False
reload: bool = False
```

### 数据库配置
```python
database_url: str = "sqlite:///./happy_partner.db"
```

### AI模型配置

#### OpenAI配置
```python
openai_api_key: str = "your-api-key"
openai_base_url: str = "https://api.deepseek.com"
openai_default_model: str = "qwen-turbo"
openai_temperature: float = 0.7
openai_max_tokens: int = 2000
openai_timeout: int = 30
```

#### Ollama配置
```python
use_ollama: bool = True
ollama_base_url: str = "http://localhost:11436"
ollama_default_model: str = "qwen2.5:0.5b"
ollama_timeout: int = 60
```

### 记忆系统配置
```python
mem0_enabled: bool = True
mem0_vector_store_provider: str = "qdrant"
mem0_qdrant_path: str = "./qdrant_db"
mem0_collection_name: str = "happy_partner"
mem0_embedding_model: str = "text-embedding-3-small"
mem0_embedding_dims: int = 1536
mem0_cache_ttl: int = 300
```

### 语音系统配置

#### TTS配置
```python
tts_provider: str = "edge-tts"  # edge-tts, gtts, pyttsx3, fish-speech, chattts
tts_voice: str = "zh-CN-XiaoxiaoNeural"
tts_rate: int = 0
tts_volume: int = 100
```

#### STT配置
```python
stt_provider: str = "whisper"  # whisper, speech_recognition
stt_model: str = "base"
stt_language: str = "zh"
```

### 多代理系统配置
```python
multi_agent_enabled: bool = True
intent_agent_enabled: bool = True
safety_agent_enabled: bool = True
emotion_agent_enabled: bool = True
edu_agent_enabled: bool = True
memory_agent_enabled: bool = True
world_agent_enabled: bool = True
role_agent_enabled: bool = True
role_factory_enabled: bool = True
chapter_manager_enabled: bool = True
```

### 故事系统配置
```python
story_max_chapters: int = 10
story_max_roles: int = 5
story_session_timeout: int = 3600
```

### 安全系统配置
```python
safety_check_enabled: bool = True
safety_filter_level: str = "strict"  # strict, moderate, lenient
safety_blocked_keywords: list = ["暴力", "色情", "赌博", "毒品", "诈骗"]
```

### 性能配置
```python
max_concurrent_requests: int = 10
request_timeout: int = 60
cache_enabled: bool = True
cache_ttl: int = 300
```

## 使用方法

### 1. 在代码中使用配置

```python
from config.settings import settings

# 使用配置
app_name = settings.app_name
port = settings.port
openai_api_key = settings.openai_api_key
```

### 2. 环境变量配置

创建 `.env` 文件：
```bash
# 复制示例文件
cp .env.example .env

# 编辑配置
OPENAI_API_KEY="your-actual-api-key"
DATABASE_URL="sqlite:///./my_happy_partner.db"
PORT=8002
```

### 3. 环境变量优先级

配置按以下优先级加载：
1. 环境变量
2. `.env` 文件
3. 默认值

## 配置示例

### 开发环境配置
```bash
# .env
DEBUG=true
RELOAD=true
LOG_LEVEL=DEBUG
OPENAI_API_KEY="your-dev-key"
```

### 生产环境配置
```bash
# .env
DEBUG=false
RELOAD=false
LOG_LEVEL=WARNING
SECRET_KEY="your-secure-production-key"
OPENAI_API_KEY="your-prod-key"
```

### 本地模型配置
```bash
# .env
USE_OLLAMA=true
OLLAMA_BASE_URL="http://localhost:11436"
OLLAMA_DEFAULT_MODEL="qwen2.5:0.5b"
```

## 配置验证

### 测试配置加载
```python
from config.settings import settings

print(f"应用名称: {settings.app_name}")
print(f"端口: {settings.port}")
print(f"数据库URL: {settings.database_url}")
```

### 运行配置测试
```bash
pytest tests/test_settings.py -v
```

## 常见问题

### 1. 配置不生效
- 检查 `.env` 文件路径是否正确
- 确认环境变量名称与配置类字段匹配
- 重启应用使配置生效

### 2. 环境变量优先级
- 系统环境变量 > `.env` 文件 > 默认值
- 使用 `export VARIABLE=value` 设置系统环境变量

### 3. 配置类型错误
- 确保环境变量值与配置字段类型匹配
- 数字类型使用纯数字，布尔类型使用 true/false

### 4. 敏感信息保护
- 不要将 `.env` 文件提交到版本控制
- 使用 `.env.example` 作为模板
- 生产环境使用系统环境变量

## 扩展配置

要添加新的配置项：

1. 在 `config/settings.py` 的 `Settings` 类中添加字段
2. 在 `.env.example` 中添加对应的环境变量示例
3. 更新测试文件 `tests/test_settings.py`
4. 在相关代码中使用新的配置项

## 配置最佳实践

1. **安全性**: 敏感信息使用环境变量
2. **可维护性**: 相关配置分组管理
3. **可测试性**: 提供默认值和测试配置
4. **文档化**: 保持配置文档更新
5. **版本控制**: 不提交敏感配置到版本控制