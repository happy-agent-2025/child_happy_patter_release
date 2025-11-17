from enum import Enum


class MessageType(Enum):
    HELLO = "hello"
    TTS = "tts"
    LLM = "llm"
    LISTEN = "listen"
    STT = "stt"
    IOT = "iot"

class MessageState(Enum):
    SENTENCE_START = "sentence_start"
    SENTENCE_END = "sentence_end"
    DETECT = "detect"
    STOP = "stop"
    START = "start"

