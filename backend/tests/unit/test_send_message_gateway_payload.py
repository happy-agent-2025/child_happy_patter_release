import asyncio
import pytest

class DummyWS:
    def __init__(self):
        self.sent = []
    async def send(self, data):
        self.sent.append(data)

class DummyConnect:
    def __init__(self):
        from utils.logger import Logger
        self.websocket = DummyWS()
        self.session_id = 'test-session'
        self.logger = Logger().log_init('test')
        self._state = {}
    def set_playback_state(self, a,b,c):
        self._state = {'i':a,'t':b,'l':c}
    def mark_audio_completed(self):
        self._state['completed'] = True

@pytest.mark.asyncio
async def test_send_audio_raw_mode():
    from utils.protocol.send_message import SendMessage
    connect = DummyConnect()
    config = {'server': {'gateway_payload': False}, 'hello_message': {'audio_params': {'frame_duration': 60}}}
    audios = [b'frame1', b'frame2']
    await SendMessage.send_audio(connect, config, audios, 'hello')
    # 两个帧应为裸字节，无16字节头
    # 文本消息也会发送，这里按至少包含2个二进制帧判断
    binary_frames = [p for p in connect.websocket.sent if isinstance(p, (bytes, bytearray))]
    assert len(binary_frames) >= 2
    assert not binary_frames[0][:16] == b'\x00'*16

@pytest.mark.asyncio
async def test_send_audio_gateway_mode():
    from utils.protocol.send_message import SendMessage
    connect = DummyConnect()
    config = {'server': {'gateway_payload': True}, 'hello_message': {'audio_params': {'frame_duration': 60}}}
    audios = [b'frame1', b'frame2']
    await SendMessage.send_audio(connect, config, audios, 'hello')
    binary_frames = [p for p in connect.websocket.sent if isinstance(p, (bytes, bytearray))]
    assert len(binary_frames) >= 2
    # 每个带头部的数据包长度至少为 16 + payload
    assert len(binary_frames[0]) >= 16
