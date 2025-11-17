import asyncio
import json
import re
import time
import uuid
from utils.protocol.messge_type import MessageState, MessageType
from utils.util import Util


class SendMessage:
    
    # 发送物联网消息
    @staticmethod
    async def send_iot_message(connect, iot_message):

        if not Util.is_valid_iot_json(iot_message):
            print("Invalid JSON format")
            return
        iot_message = re.sub(r'\s+', '', iot_message) # 去除多余的空格，可以节省带宽
        frame_id = str(uuid.uuid4().hex)
        msg = {
            "type": MessageType.IOT.value,
            "session_id": connect.session_id,
            "text": json.loads(iot_message),
            "frame_id": frame_id
        }
        await connect.websocket.send(json.dumps(msg))
    
    # 发送文本消息
    @staticmethod
    async def _send_stt_text(connect, text):
        msg = {
            "type":MessageType.STT.value,
            "session_id": connect.session_id,
            "text": text
        }
        connect.websocket.send(json.dumps(msg)) # 先把识别到的文字给到前端
        
    @staticmethod
    async def send_hello_message(connect, config):
        """发送 hello 消息"""
        hello_message = config["hello_message"]
        hello_message["session_id"] = connect.session_id # session_id 每次都不能变
        await connect.websocket.send(json.dumps(hello_message)) # 把文本转换成json格式发送给前端
    
    # 组装音频之前的文字消息
    @staticmethod
    async def _send_audio_text(connect, type, state, text = ""):
        message = {
            "type": type,
            "session_id": connect.session_id,
            "state":state,
            "text": text
        }
        
        if text == "":
            del message["text"]
        await connect.websocket.send(json.dumps(message))
    
    # 发送音频   
    @staticmethod
    async def send_audio(connect, config, audios, reponse):
        
        # 问答结束返回
        if not reponse:
            await SendMessage._send_audio_text(connect, MessageType.TTS.value, MessageState.SENTENCE_END.value, "TTS结束")
            return
        
        # 发送后端音频开始
        await SendMessage._send_audio_text(connect, MessageType.TTS.value, MessageState.SENTENCE_START.value, reponse)
        
        """发送音频消息，主要处理要分段，计算每一段的长度，然后发送"""
        frame_duration = config["hello_message"]["audio_params"]["frame_duration"]
        frame_s = frame_duration / 1000
        start_time = time.perf_counter()
        i = 0

        # 处理音频数据，每个报数据段开始发送，每段时长为frame_duration
        for opus_packet in audios:
            if i >= 2:
                expected_end_time = start_time + ((i + 1) * frame_s)
                current_time = time.perf_counter()
                remaining_time = expected_end_time - current_time
                if remaining_time > 0:
                    await asyncio.sleep(remaining_time)
            
            # 发送帧数据
            await connect.websocket.send(opus_packet)
            i += 1
        
        # 发送后端音频结束
        await SendMessage._send_audio_text(connect, MessageType.TTS.value, MessageState.SENTENCE_END.value, "TTS结束")