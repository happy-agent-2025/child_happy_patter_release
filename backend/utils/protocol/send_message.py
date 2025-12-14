import asyncio
import json
import re
import time
import uuid
from utils.protocol.messge_type import MessageState, MessageType
from utils.util import Util


class SendMessage:
       
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
    async def send_audio(connect, config, audios, reponse, current_index=None, total_sentences=None, is_last_sentence=None, task_id=None):

        # 问答结束返回
        if not reponse or not audios:
            await SendMessage._send_audio_text(connect, MessageType.TTS.value, MessageState.STOP.value, "TTS结束")
            return

        # 发送后端音频开始
        await SendMessage._send_audio_text(connect, MessageType.TTS.value, MessageState.SENTENCE_START.value, reponse)

        # 在音频播放开始时设置播放状态
        if current_index is not None and total_sentences is not None and is_last_sentence is not None:
            connect.set_playback_state(current_index, total_sentences, is_last_sentence)

        """发送音频消息，主要处理要分段，计算每一段的长度，然后发送"""
        frame_duration = config["hello_message"]["audio_params"]["frame_duration"]
        frame_s = frame_duration / 1000

        await SendMessage._send_audio_text(connect, MessageType.TTS.value, MessageState.START.value, "TTS开始")
        # 计算音频总时长
        total_audio_duration = len(audios) * frame_s
        start_time = time.perf_counter()
        i = 0

        # 处理音频数据，每个报数据段开始发送，每段时长为frame_duration
        timestamp = 0
        for opus_packet in audios:
            if i >= 5:
                expected_end_time = start_time + ((i + 1) * frame_s)
                current_time = time.perf_counter()
                remaining_time = expected_end_time - current_time
                if remaining_time > 0:
                    await asyncio.sleep(remaining_time)

                timestamp = int((start_time + i * frame_duration / 1000) * 1000) % (
                    2**32
                )

            # 发送帧数据
            await connect.websocket.send(opus_packet)
            # await SendMessage._send_to_websocket_gateway(connect, opus_packet, timestamp, i)
            i += 1

        # 关键修复：等待音频播放完成
        elapsed_time = time.perf_counter() - start_time
        remaining_play_time = total_audio_duration - elapsed_time
        if remaining_play_time > 0:
            # 等待剩余的音频播放时间
            await asyncio.sleep(remaining_play_time)

        # 标记音频播放完成
        await connect.mark_audio_completed()

        # 发送后端音频结束
        # await SendMessage._send_audio_text(connect, MessageType.TTS.value, MessageState.STOP.value, "TTS结束")
    
    @staticmethod
    async def _send_to_websocket_gateway(connect, opus_packet, timestamp, sequence):
        """
        发送带16字节头部的opus数据包给websocket_gateway
        Args:
            conn: 连接对象
            opus_packet: opus数据包
            timestamp: 时间戳
            sequence: 序列号
        """
        # 为opus数据包添加16字节头部
        header = bytearray(16)
        header[0] = 1  # type
        header[2:4] = len(opus_packet).to_bytes(2, "big")  # payload length
        header[4:8] = sequence.to_bytes(4, "big")  # sequence
        header[8:12] = timestamp.to_bytes(4, "big")  # 时间戳
        header[12:16] = len(opus_packet).to_bytes(4, "big")  # opus长度

        # 发送包含头部的完整数据包
        complete_packet = bytes(header) + opus_packet
        await connect.websocket.send(complete_packet)