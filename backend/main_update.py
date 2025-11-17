import asyncio
import os
from ai_core.ai_instance_repository import AiInstanceRepository
from utils.protocol.websocket_server import WebSocketServer
from utils.ai_factory.ai_factory import AIFactory
from utils.util import Util

# 主程序越简单越好
if __name__ == "__main__":
    
    config = Util.get_config()
    ai = AiInstanceRepository(config)

    server = WebSocketServer(config, ai)
    try:
        asyncio.run(server.start()) # 异步运行服务器
    except KeyboardInterrupt:
        print("WebSocket服务器已停止") 
        
        
        
        