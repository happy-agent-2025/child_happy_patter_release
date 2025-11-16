from datetime import datetime
import json
import time
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 在导入任何模块之前配置警告
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 配置日志
from config.warnings_config import configure_logging
configure_logging()

# 导入全局异常处理
from core.exceptions import setup_exception_handlers

# 初始化数据库
from utils.db import init_db

success = init_db.init_db()
if not success:
    print("数据库初始化失败")
else:
    print("数据库初始化成功")

# 导入路由
from api.langgraph_routes import router as langgraph_router

from config.settings import settings

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    openapi_url="/openapi.json",
    docs_url=None,
    redoc_url=None
)

# 设置全局异常处理
setup_exception_handlers(app)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# 包含路由
app.include_router(langgraph_router, prefix="/api")

# 本地接口文档（Scalar），无需外网
app.get("/api-docs", include_in_schema=False)(
    get_scalar_api_reference(
        openapi_url="/openapi.json",
        title="Happy Partner API Docs"
    )
)

@app.get("/")
async def root():
    return {
        "message": "儿童故事互动AI系统API服务",
        "version": "2.0.0",
        "features": [
            "智能聊天",
            "故事创作",
            "角色扮演",
            "记忆管理",
            "情感分析",
            "安全检查",
        ],
        "api_endpoints": {
            "chat": "/api/langgraph/chat",
            "workflow_state": "/api/langgraph/workflow/state",
            "analytics": "/api/langgraph/analytics/conversation-flow",
            "session": "/api/langgraph/session",
        },
    }


# ota请求处理
@app.post("/xiaozhi/ota")
async def ota_check(request: Request):
    """OTA版本检查接口"""
    try:
        headers = dict(request.headers)
        body = await request.body()

        print('OTA检查请求:')
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
        response = {
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
        print('OTA响应:', response)
        return response

    except Exception as e:
        print(f"[ERROR] OTA接口处理失败: {e}")
        import traceback
        print(f"[ERROR] 详细错误信息: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"OTA检查失败: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket通信接口 - 智能分发音频和文本消息"""
    await websocket.accept()

    audio_session_id = None
    status = None

    try:
        # 保持连接并处理后续消息 - 智能分发
        while True:
            data = await websocket.receive()

            if data['type'] == 'websocket.receive':
                
                if not hasattr(data, "get"):
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>", data)
                    continue
                
                message_data = data.get('text') or data.get('bytes')

                if isinstance(message_data, str):
                    # 智能分发：文本消息 -> 文本处理
                    status = await _handle_text_message(message_data, websocket)
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", message_data)
  
                elif isinstance(message_data, bytes):
                    # 智能分发：二进制消息 -> 音频处理
                    # audio_session_id = _audio_start_session("unknow")
                    print(f"Received audio from device {audio_session_id}")
                    # await _handle_audio_message(audio_session_id, message_data, websocket)

            elif data['type'] == 'websocket.disconnect':
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[ERROR] WebSocket错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        
        # 清理资源
            
        # if audio_session_id != "Session_Audio_Unknown" and audio_session_id:
            # audio_manager.end_session(audio_session_id) 

        print(f"[DISCONNECT] 设备 {audio_session_id} 关闭")

async def _handle_text_message(message_data: str, websocket: WebSocket) -> dict[str, any]: # type: ignore
    """处理文本消息 - 智能分发到文本处理逻辑"""
    
    device_id = "Unknown"
    
    try:
        message = json.loads(message_data)

        if message.get('type') == 'hello':
            # 设备hello消息
            device_id = message.get('device_id') or 'Unknown'

            # 处理hello消息
            response = protocol_handler.handle_hello_message(device_id, message)

            # 连接WebSocket
            await websocket_manager.connect(websocket, device_id)

            # 发送欢迎消息
            await websocket.send_json(response)

            print(f"[CONNECT] 设备 {device_id} 已连接到WebSocket", response.get("session_id"))
            print(message)
            
            return {
                        "status": "success",
                        "device_id": device_id,
                        "session_id": response.get("session_id"),
                    }
        elif message.get('type') == "listen":
            if message.get('state') == "detect":
                
                
                return{
                            "status": "success",
                            "type": "listen",
                            # "session_id": response.get("session_id"),
                        }
        else:
            return {
                        "status": "error",
                        "device_id": None,
                        "session_id": None,
                    }

    except json.JSONDecodeError:
        print(f"[ERROR] 无法解析JSON消息: {message_data}")
        return {
                    "status": "error",
                    "device_id": None,
                    "session_id": None,
                }
    except Exception as e:
        print(f"[ERROR] 处理文本消息失败: {e}")
        return {
                    "status": "error",
                    "device_id": None,
                    "session_id": None,
                }
        
@app.post("/xiaozhi/ota/activate")
async def activate_device(request: Request):
    """设备激活接口"""
    headers = dict(request.headers)
    activation_data = await request.json()

    print('[ACTIVATION] 激活请求:')
    print(f'  头信息: {headers}')
    print(f'  请求体: {activation_data}')

    device_id = headers.get('device-id')

    if not device_id:
        print(f"[ERROR] 缺少设备ID")
        raise HTTPException(status_code=400, detail="缺少设备ID")

    # 发送激活成功消息到WebSocket
    try:
        await websocket_manager.send_personal_message({
            'type': 'device_activated',
            'device_id': device_id,
            'message': '设备激活成功',
            'timestamp': datetime.now().isoformat()
        }, device_id)
    except Exception as e:
        print(f"[WARNING] 无法发送WebSocket消息: {e}")

    return {
        'success': True,
        'message': '设备激活成功',
        'activated_at': datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn

    # 使用配置中的服务器设置
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )
