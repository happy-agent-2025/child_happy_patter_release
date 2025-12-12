# 协议与音频链路演进时间线

## 时间线里程碑
- 2025-11-23 合入多智能体逻辑与双服务入口（commit `0540447`）
  - 入口：`main_update.py` 引导 WebSocket 与 aiohttp HTTP 并行
  - 协议层统一：`utils/protocol/http_server.py` OTA/健康接口
- 2025-11-23 数据库集成与 Agents TDD（commit `d2a8df3`）
  - 引入 SQLite + SQLAlchemy：`utils/db/database.py`、`utils/db/models.py`、`utils/db/database_service.py`
- 2025-11-24 LLM provider 统一（commit `1adc144`、`386027a`）
  - DeepSeek 通过 OpenAI 兼容客户端：`ai_core/llm/openai.py`
- 2025-11-25 分句与消息处理增强（commit `5edc9bd`）
  - 分句器：`utils/sentence_splitter.py`；消息路由：`utils/protocol/message_process.py`
- 2025-11-25 并发修复（commit `d7dde7c`）
  - 并发稳定性增强：`utils/protocol/message_process.py`
- 2025-11-26 队列状态检测（commit `a3f41c6`）
  - 播放监控与任务状态：`utils/protocol/connect_process.py`
- 2025-11-29 句子信息集成至音频队列（commit `23f6947`）
  - 统一把 `current_index/total_sentences/is_last_sentence` 打包：`utils/protocol/connect_process.py`
- 2025-11-29 播放完成信号修复（commit `4361120`）
  - 最后一条音频完成后发送完成信号路径修复：`utils/protocol/connect_process.py`

## 当前实现要点与代码定位
- 入口与运行
  - 并发启动：`main_update.py:27-31`
  - 启动校验与建表：`main_update.py:12-16`
- 配置系统
  - 加载与环境变量覆盖：`utils/util.py:90-96`、`utils/util.py:141-183`
  - 启动校验：`utils/util.py:185-229`
- 健康接口
  - 返回版本、uptime、组件状态与依赖可用性：`utils/protocol/http_server.py:119-141`
  - 服务器启动时间记录：`utils/protocol/http_server.py:136-139`
- 音频链路
  - TTS 生成：`ai_core/tts/edge.py:12-36`
  - Opus 编码：`utils/audio_format/opus.py:26-67`
  - 帧发送（裸帧/网关包）切换：`utils/protocol/send_message.py:96-106`
  - 播放完成标记与信号：`utils/protocol/send_message.py:112-117`、`utils/protocol/connect_process.py:358-368`、`utils/protocol/connect_process.py:392-400`

## 行为变化与默认值
- 帧协议：默认发送“裸 Opus 帧”；如接收端需要 16 字节头部，设置 `server.gateway_payload: true` 使用 `_send_to_websocket_gateway`。
- 健康返回：增加 `components.env.opuslib_next_available` 与 `ffmpeg_available` 便于排障。
- 配置：支持环境变量覆盖（无前缀或 `APP_` 前缀），并在启动进行关键项校验。

## 风险与兼容性
- 依赖：`opuslib_next` 与本机 `ffmpeg` 必须可用，否则编码或加载会失败。
- 文本清理为空时会产生空音频（`ai_core/tts/base.py:20-40`），需确保输入文本合理。
- 前后端协议对齐：如出现“未收到音频”，优先确认接收端是否需要带头部包格式。

## 最小验证
- 健康检查：`GET http://localhost:3000/health`，确认版本、组件状态与依赖可用性。
- 帧协议切换：在 `data/config.yaml` 设置 `server.gateway_payload: true/false`，验证前端是否正确播放。

