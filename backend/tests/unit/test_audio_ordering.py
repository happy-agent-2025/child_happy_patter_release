import asyncio
import threading
import time
import json

class DummyWebSocket:
    def __init__(self):
        self.sent = []
    async def send(self, data):
        self.sent.append(data)

def tts_func(i, delay):
    time.sleep(delay)
    return [b"frame"], 0.02, f"sentence_{i}"

def extract_sentence_starts(sent_list):
    starts = []
    for item in sent_list:
        if isinstance(item, str):
            try:
                msg = json.loads(item)
                if msg.get("type") == "tts" and msg.get("state") == "sentence_start" and "text" in msg:
                    starts.append(msg["text"])
            except Exception:
                pass
    return starts

def test_ordering_flush(monkeypatch):
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from utils.protocol.connect_process import ConnectProcess

    class DummyAI:
        def __init__(self):
            pass

    config = {"hello_message": {"audio_params": {"frame_duration": 20}}}
    connect = ConnectProcess(config, DummyAI())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    connect.loop = loop
    connect.websocket = DummyWebSocket()

    th = threading.Thread(target=connect._audio_send_thread, daemon=True)
    th.start()

    # 3 句，故意乱序完成：索引0(0.3s)→1(0.1s)→2(0.2s)
    fut0 = connect.connect_thread_pool.submit(tts_func, 0, 0.3)
    fut1 = connect.connect_thread_pool.submit(tts_func, 1, 0.1)
    fut2 = connect.connect_thread_pool.submit(tts_func, 2, 0.2)

    info0 = {"current_index":0, "total_sentences":3, "is_last_sentence":False}
    info1 = {"current_index":1, "total_sentences":3, "is_last_sentence":False}
    info2 = {"current_index":2, "total_sentences":3, "is_last_sentence":True}

    connect.enqueue_audio_task(fut0, info0)
    connect.enqueue_audio_task(fut1, info1)
    connect.enqueue_audio_task(fut2, info2)

    time.sleep(2.0)
    connect.stop_event.set()
    loop.run_until_complete(asyncio.sleep(0.05))

    starts = extract_sentence_starts(connect.websocket.sent)
    assert starts == ["sentence_0", "sentence_1", "sentence_2"]
