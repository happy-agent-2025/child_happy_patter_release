import asyncio
import os
from ai_core.ai_instance_repository import AiInstanceRepository
from utils.protocol.websocket_server import WebSocketServer
from utils.protocol.http_server import create_http_server
from utils.ai_factory.ai_factory import AIFactory
from utils.util import Util


async def main():
    """主异步函数，同时启动 WebSocket 和 HTTP 服务器"""
    config = Util.get_config()
    ai = AiInstanceRepository(config)

    # 启动 WebSocket 服务器
    ws_server = WebSocketServer(config, ai)

    # 启动 HTTP 服务器（OTA 服务）
    http_server = await create_http_server(
        config,
        host="0.0.0.0",
        port=3000  # 使用 8080 端口，避免与 FastAPI 冲突
    )

    try:
        # 同时运行两个服务器
        await asyncio.gather(
            ws_server.start(),
            # HTTP 服务器已经在 create_http_server 中启动，这里只需要保持运行
            asyncio.sleep(float('inf'))  # 无限等待
        )
    except KeyboardInterrupt:
        print("正在停止服务器...")
        await http_server.stop()
        print("所有服务器已停止")


# 主程序
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("程序已终止") 
        
        
        
        