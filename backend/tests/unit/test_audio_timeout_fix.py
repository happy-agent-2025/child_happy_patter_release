import asyncio
import threading
import time

class DummyWebSocket:
    def __init__(self):
        self.sent = []
        self.closed = False
    async def send(self, data):
        self.sent.append(data)
    async def recv(self):
        await asyncio.sleep(0.01)
        return b""
    async def close(self):
        self.closed = True

def test_audio_send_no_timeout(monkeypatch):
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from utils.protocol.connect_process import ConnectProcess
    from ai_core.ai_instance_repository import AiInstanceRepository

    config = {
        "hello_message": {
            "audio_params": {
                "frame_duration": 20
            }
        },
        "tts_timeout_seconds": 30
    }

    class DummyAI(AiInstanceRepository):
        def __init__(self):
            self.asr = None
            class TTS:
                def text_to_opus_data(self, text):
                    time.sleep(0.1)
                    return [b"x"], 0.02, text or ""
            self.tts = TTS()
            self.llm = None
            self.vad = None

    ai = DummyAI()
    connect = ConnectProcess(config, ai)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    connect.loop = loop
    connect.websocket = DummyWebSocket()

    thread = threading.Thread(target=connect._audio_send_thread, daemon=True)
    thread.start()

    fut = connect.connect_thread_pool.submit(connect.ai.tts.text_to_opus_data, "hello")
    sentence_info = {"current_index":0, "total_sentences":1, "is_last_sentence":True}
    connect.enqueue_audio_task(fut, sentence_info)

    time.sleep(0.5)
    connect.stop_event.set()
    loop.run_until_complete(asyncio.sleep(0.05))

    assert any(isinstance(x, (bytes, bytearray)) for x in connect.websocket.sent)
