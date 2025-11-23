# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the backend for "Happy Partner" - a children's education AI system that provides real-time voice interaction capabilities. The system uses WebSocket for real-time communication and HTTP for OTA services, with a multi-agent architecture powered by LangGraph.

## Architecture

### Core Components

- **WebSocket Server** (`utils/protocol/websocket_server.py`): Real-time voice and message communication on port 3001
- **HTTP Server** (`utils/protocol/http_server.py`): OTA services and health checks on port 3000
- **AI Instance Repository** (`ai_core/ai_instance_repository.py`): Manages AI service instances (ASR, TTS, LLM, VAD)
- **AI Factory** (`utils/ai_factory/ai_factory.py`): Factory pattern for creating AI components
- **Connect Process** (`utils/protocol/connect_process.py`): Handles individual WebSocket connections
- **Message Process** (`utils/protocol/message_process.py`): Routes and processes different message types

### AI Components

- **ASR (Speech Recognition)**: FunASR model for Chinese speech-to-text
- **TTS (Text-to-Speech)**: EdgeTTS service for Chinese speech synthesis
- **LLM (Language Model)**: DeepSeek model for text understanding and generation
- **VAD (Voice Activity Detection)**: Silero model for detecting speech start/end

### Multi-Agent System

The system uses a LangGraph-based multi-agent architecture:
- **Role Agent**: Manages character roles and personalities
- **World Agent**: Handles world state and context
- **Memory Agent**: Manages conversation memory using Mem0
- **Safety Agent**: Ensures content safety and appropriateness
- **Emotion Agent**: Detects and responds to emotional cues
- **Intent Agent**: Classifies user intent

## Development Commands

### Running the Application
```bash
# Start the main application (WebSocket + HTTP servers)
python main_update.py

# Run with specific configuration
python main_update.py --config_path data/config.yaml
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_langgraph_routes_real.py

# Run LangGraph real interface tests
python run_real_langgraph_tests.py
```

### Configuration

Main configuration file: `data/config.yaml`
- Server settings (ports, host)
- Model selection (TTS, ASR, LLM, VAD)
- API keys and service endpoints
- Audio parameters (sample rate, format)

## Key Implementation Patterns

### Concurrency Model
- **asyncio** for I/O-bound operations (WebSocket, HTTP)
- **ThreadPoolExecutor** for CPU-bound tasks (max_workers=10)
- **Queue-based communication** between threads
- **Cross-thread coroutine execution** using `asyncio.run_coroutine_threadsafe`

### Message Processing Flow
1. Client audio → WebSocket → VAD detection → ASR recognition → LLM processing → TTS synthesis → Return to client
2. Text messages are routed based on JSON message types (HELLO, LISTEN, START, STOP)

### Error Handling
- Global exception handling in main loop
- Connection-level exception handling with resource cleanup
- Graceful shutdown on KeyboardInterrupt
- Timeout controls to prevent infinite waits

## File Structure

```
backend/
├── agents/                 # Multi-agent system components
├── ai_core/               # Core AI services (ASR, TTS, LLM, VAD)
├── data/                  # Configuration files
├── docs/                  # Documentation
├── model/                 # AI model files
├── utils/                 # Utility modules
│   ├── protocol/          # WebSocket and HTTP protocol handlers
│   ├── ai_factory/        # AI component factory
│   └── audio_format/      # Audio processing utilities
├── main_update.py         # Main application entry point
└── requirements.txt       # Python dependencies
```

## Important Notes

- The system is designed for Chinese language interaction
- WebSocket connections are stateful and maintain conversation context
- Audio data is processed in real-time using Opus format
- Memory is managed per connection using Mem0 for persistence
- Configuration uses YAML format with environment-specific settings

## Development Guidelines

- Use async/await for all I/O operations
- Follow the factory pattern for AI component creation
- Implement proper resource cleanup in connection handlers
- Use the logger utility for consistent logging
- Maintain separation between protocol handling and AI processing
- Use the `langgraph` package for LangGraph-based multi-agent system