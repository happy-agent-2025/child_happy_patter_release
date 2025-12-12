# 配置与协议速查

## 关键配置
- `server.port`：WebSocket 端口，默认 `3001`
- `server.websocket_url`：WebSocket 地址，例如 `ws://<host>:3001/ws`
- `server.gateway_payload`：音频帧发送模式
  - `false`：发送裸 Opus 帧（默认）
  - `true`：发送带 16 字节头的网关数据包（`utils/protocol/send_message.py:119-138`）
- `select_model`：选择 `TTS/ASR/LLM/VAD`
- `LLM.openai.api_key/base_url`：OpenAI 兼容客户端（DeepSeek）所需参数

## 环境变量覆盖
- 规则：把配置路径转换为大写并用下划线连接
  - 示例：`LLM.openai.api_key` → `LLM_OPENAI_API_KEY` 或 `APP_LLM_OPENAI_API_KEY`
- 类型转换：按原值类型自动转换；复杂结构用 JSON 字符串覆盖
- 加载流程：`utils/util.py:90-96` → `utils/util.py:141-183`
- 启动校验：`utils/util.py:185-229`

## 健康检查
- 端点：`GET /health`
- 字段：
  - `version`、`uptime_seconds`、`components.LLM/TTS/ASR/VAD`
  - `components.env.opuslib_next_available`、`ffmpeg_available`（`utils/protocol/http_server.py:119-141`）

## 音频帧协议
- 裸帧发送（默认）：`utils/protocol/send_message.py:100-104`
- 网关包发送（16 字节头）：`utils/protocol/send_message.py:96-106`（根据 `server.gateway_payload` 切换）
- 网关包格式：`utils/protocol/send_message.py:119-138`

## 快速验证
- 健康：`curl http://localhost:3000/health`
- 帧模式切换：编辑 `data/config.yaml` 的 `server.gateway_payload`，观察前端接收状态
- 依赖检查：确保安装 `opuslib_next` 与系统 `ffmpeg`

