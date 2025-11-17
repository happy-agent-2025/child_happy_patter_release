import asyncio
import traceback
import websockets
from ai_core.ai_instance_repository import AiInstanceRepository
from utils.protocol.connect_process import ConnectProcess
from utils.logger import Logger
from utils.util import Util

TAG = __name__

class WebSocketServer:
    
    # RAII 原则，初始化接口
    def __init__(self, config, ai:AiInstanceRepository):
        self.websocket= None
        self.config = config
        self.ai = ai
        self.logger = Logger().log_init(TAG)

    # async 函数，含义是异步，会返回一个协程对象
    async def start(self):
        host = self.config["server"]["host"]
        port = self.config["server"]["port"]
        async with websockets.serve(self.handle_connection, host, port):
            self.logger.info(f"WebSocket服务器已启动，监听地址：{host}:{port}")
            await asyncio.Future()

    # 处理连接，连接成功之后会走的处理函数
    async def handle_connection(self, websocket):
        connect_process = ConnectProcess(self.config, self.ai)
        await connect_process.connect(websocket)