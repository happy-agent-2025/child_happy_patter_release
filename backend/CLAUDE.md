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

The system uses a sophisticated LangGraph-based multi-agent architecture with two main workflows:

#### LangGraph Workflow (`agents/langgraph_workflow.py`)
A comprehensive state-based workflow that manages the complete conversation lifecycle:
- **State Management**: Uses `AgentState` TypedDict to track conversation state
- **Node-based Processing**: Sequential processing through specialized nodes
- **Conditional Routing**: Dynamic routing based on intent and safety checks
- **Memory Integration**: Real-time memory updates and context enrichment

**Key Nodes in Workflow:**
- `input_processing`: Input validation and initialization
- `context_enrichment`: Intelligent context injection and user profile building
- `safety_check`: Two-layer safety filtering (keyword + AI analysis)
- `intent_analysis`: Intent classification using MetaAgent
- `route_agent`: Dynamic agent routing based on intent
- `edu_agent`: Educational content processing
- `emotion_agent`: Emotional interaction handling
- `memory_update`: LangGraph memory management
- `context_summary`: Periodic conversation summarization

#### Multi-Agent State Graph (`agents/multi_agent.py`)
A more complex state graph supporting multiple interaction modes:
- **Interaction Modes**: Chat mode vs Story mode
- **Voice Integration**: Support for voice input/output processing
- **Story Sessions**: Complete story world and role management
- **Memory Persistence**: Integration with Mem0 memory system

**Specialized Agents:**
- **Role Agent** (`agents/role_agent.py`): Character role-playing with personality consistency, emotion expression, and educational value extraction
- **Intent Agent** (`agents/intent_agent.py`): Enhanced intent recognition with wake-up word detection, keyword analysis, and AI-powered classification
- **Safety Agent** (`agents/safety_agent.py`): Two-layer content filtering (keyword pre-filter + AI analysis) with child-friendly safety guidelines
- **Memory Agent** (`agents/memory_agent.py`): Conversation history management with automatic summarization and context retrieval
- **Emotion Agent**: Emotional state detection and appropriate response generation
- **World Agent**: Story world creation and management
- **Chapter Manager**: Story progression and chapter management

## Agent System Technologies

### Core Technologies

**LangGraph Framework**:
- **State Graphs**: TypedDict-based state management with type safety
- **Conditional Edges**: Dynamic routing based on state conditions
- **Node Composition**: Modular node design for specialized processing
- **Asynchronous Processing**: Full async/await support for I/O operations

**Memory Management**:
- **Mem0 Integration**: Persistent memory storage for user profiles and conversation history
- **Context Enrichment**: Intelligent context injection based on conversation history
- **User Profiling**: Dynamic user profile building from interaction patterns
- **Conversation Summarization**: Automatic summarization of long conversations

**Safety and Content Filtering**:
- **Two-Layer Filtering**: Keyword pre-filter + AI-powered content analysis
- **Child-Friendly Guidelines**: Comprehensive safety guidelines for children's content
- **Real-time Filtering**: Immediate content validation during conversation flow

**Intent Recognition**:
- **Multi-Modal Analysis**: Keyword matching + AI classification + entity extraction
- **Wake-up Word Detection**: Support for voice activation and mode switching
- **Emotion Integration**: Emotional context consideration in intent analysis

**Role-Playing System**:
- **Character Consistency**: Personality and background consistency maintenance
- **Emotional Expression**: Dynamic emotional state management for characters
- **Educational Value**: Automatic extraction of learning points from interactions
- **Story Progression**: Chapter-based story management and progression

### Design Patterns

**Factory Pattern**:
- `AIFactory` for AI component creation (ASR, TTS, LLM, VAD)
- `RoleFactory` for dynamic role agent creation

**State Pattern**:
- `AgentState` for conversation state management
- `GraphState` for multi-agent workflow state

**Observer Pattern**:
- Memory updates trigger context enrichment
- Safety checks trigger content filtering

**Strategy Pattern**:
- Different processing strategies for chat vs story modes
- Multiple intent classification strategies

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
- After completing a phase of functionality and passing the unit tests, it must be committed to the local repository using git
- The principles of single responsibility, low coupling, and high cohesion must be strictly maintained in functions
- Before starting feature development, a detailed plan must be submitted for my review and confirmation. Actual development may only begin after approval is granted

### General Guidelines
- Use async/await for all I/O operations
- Follow the factory pattern for AI component creation
- Implement proper resource cleanup in connection handlers
- Use the logger utility for consistent logging
- Maintain separation between protocol handling and AI processing

### Agent System Guidelines
- Use the `langgraph` package for LangGraph-based multi-agent system
- Define clear state schemas using TypedDict for type safety
- Implement proper error handling in all agent nodes
- Use conditional edges for dynamic routing based on state
- Maintain agent state consistency across the workflow
- Implement memory persistence for long-term context
- Follow the two-layer safety filtering approach (keyword + AI)
- Use factory patterns for dynamic agent creation
- Implement proper locking for thread-safe agent operations
- Provide comprehensive metadata in agent responses

### Testing Guidelines
- Test individual agent nodes in isolation
- Test complete workflow execution paths
- Test error conditions and recovery mechanisms
- Test memory persistence and context retrieval
- Test safety filtering with various input types