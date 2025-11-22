"""
OTA 请求处理器
提供与 FastAPI 版本兼容的 OTA 检查功能
"""

import time
import traceback
from typing import Dict, Any

from config.settings import settings


class OTAHandler:
    """OTA 请求处理器类"""

    @staticmethod
    async def process_ota_request(headers: Dict[str, str], body: bytes) -> Dict[str, Any]:
        """
        处理 OTA 检查请求

        Args:
            headers: 请求头信息
            body: 请求体数据

        Returns:
            OTA 响应数据
        """
        try:
            print('OTA检查请求处理:')
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
                    'url': settings.websocket_url,
                    'token': settings.websocket_token,
                    'reconnect': settings.websocket_reconnect,
                    'version': settings.websocket_version
                }
            }
            print('OTA响应数据:', response_data)

            return response_data

        except Exception as e:
            print(f"[ERROR] OTA请求处理失败: {e}")
            print(f"[ERROR] 详细错误信息: {traceback.format_exc()}")
            raise

    @staticmethod
    def get_websocket_config() -> Dict[str, Any]:
        """
        获取 WebSocket 配置信息

        Returns:
            WebSocket 配置字典
        """
        return {
            'url': settings.websocket_url,
            'token': settings.websocket_token,
            'reconnect': settings.websocket_reconnect,
            'version': settings.websocket_version
        }

    @staticmethod
    def get_server_time() -> Dict[str, Any]:
        """
        获取服务器时间信息

        Returns:
            服务器时间信息字典
        """
        return {
            'ts': int(time.time() * 1000),
            'tz': 480  # 东八区，单位：分钟
        }