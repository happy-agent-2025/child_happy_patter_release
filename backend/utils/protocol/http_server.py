"""
aiohttp HTTP 服务器实现
提供 OTA 相关接口，与现有 WebSocket 服务并行运行
"""

import asyncio
import time
import traceback
from typing import Dict, Any
import aiohttp
from aiohttp import web
import json


class HTTPServer:
    """aiohttp HTTP 服务器类"""

    def __init__(self, config, host: str = "0.0.0.0", port: int = 8080):
        """
        初始化 HTTP 服务器

        Args:
            host: 监听地址
            port: 监听端口
        """
        self.host = host
        self.port = port
        self.config = config
        self.app = web.Application()
        self.runner = None
        self.site = None

        # 设置路由
        self._setup_routes()

        # 设置中间件
        self._setup_middleware()

    def _setup_routes(self):
        """设置路由"""
        # OTA 检查接口
        self.app.router.add_post('/xiaozhi/ota', self.ota_check)

        # 健康检查接口
        self.app.router.add_get('/health', self.health_check)

    def _setup_middleware(self):
        """设置中间件"""

        async def cors_middleware(app, handler):
            """CORS 中间件"""
            async def middleware_handler(request):
                if request.method == 'OPTIONS':
                    response = web.Response()
                else:
                    response = await handler(request)

                # 设置 CORS 头
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, device-id, client-id, user-agent'

                return response
            return middleware_handler

        self.app.middlewares.append(cors_middleware)

    async def ota_check(self, request: web.Request) -> web.Response:
        """
        OTA 版本检查接口
        保持与 FastAPI 版本相同的响应格式
        """
        try:
            headers = dict(request.headers)
            body = await request.read()

            print('OTA检查请求 (aiohttp):')
            print(f'  方法: {request.method}')
            print(f'  头信息: {headers}')

            try:
                body_text = body.decode('utf-8') if body else "空"
                print(f'  请求体: {body_text}')
            except Exception as e:
                print(f'  请求体解码错误: {e}')

            # 获取设备信息
            device_id = headers.get('device-id', 'unknown')
            client_id = headers.get('client-id', 'unknown')
            user_agent = headers.get('user-agent', '')

            print(f'  设备信息: device_id={device_id}, client_id={client_id}, user_agent={user_agent}')

            # 构建响应 - 使用简短的字段名避免NVS键名过长
            response_data = {
                'server_time': {
                    'ts': int(time.time() * 1000),
                    'tz': 480  # 东八区，单位：分钟
                },
                'websocket': {
                    'url': self.config["server"]["host"],
                    'token': self.config["server"]["port"],
                    'reconnect': self.config["server"]["reconnect_interval"],
                    'version': self.config["server"]["version"]
                }
            }
            print('OTA响应 (aiohttp):', response_data)

            return web.json_response(response_data)

        except Exception as e:
            print(f"[ERROR] OTA接口处理失败 (aiohttp): {e}")
            print(f"[ERROR] 详细错误信息: {traceback.format_exc()}")
            return web.json_response(
                {'error': f'OTA检查失败: {str(e)}'},
                status=500
            )

    async def health_check(self, request: web.Request) -> web.Response:
        """健康检查接口"""
        return web.json_response({
            'status': 'healthy',
            'timestamp': int(time.time()),
            'service': 'aiohttp-ota-server'
        })

    async def start(self):
        """启动 HTTP 服务器"""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()

            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()

            print(f"aiohttp HTTP 服务器启动成功")
            print(f"  地址: http://{self.host}:{self.port}")
            print(f"  OTA接口: http://{self.host}:{self.port}/xiaozhi/ota")
            print(f"  健康检查: http://{self.host}:{self.port}/health")

        except Exception as e:
            print(f"[ERROR] 启动 aiohttp HTTP 服务器失败: {e}")
            raise

    async def stop(self):
        """停止 HTTP 服务器"""
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            print("aiohttp HTTP 服务器已停止")
        except Exception as e:
            print(f"[ERROR] 停止 aiohttp HTTP 服务器失败: {e}")


async def create_http_server(config, host: str = "0.0.0.0", port: int = 8080) -> HTTPServer:
    """
    创建并启动 HTTP 服务器

    Args:
        host: 监听地址
        port: 监听端口

    Returns:
        HTTPServer 实例
    """
    server = HTTPServer(config, host, port)
    await server.start()
    return server