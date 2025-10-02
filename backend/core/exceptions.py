"""
统一异常处理模块
符合项目规范：避免敏感错误信息直接暴露给客户端
"""

from typing import Dict, Any, Optional
import logging
import traceback
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class AudioProcessingError(Exception):
    def __init__(self, message: str, error_code: str = "AUDIO_ERROR", details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class STTError(Exception):
    def __init__(self, message: str, error_code: str = "STT_ERROR", details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class TTSError(Exception):
    def __init__(self, message: str, error_code: str = "TTS_ERROR", details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class SafeExceptionHandler:
    """安全的异常处理器 - 避免敏感信息泄露"""
    
    @staticmethod
    def get_safe_error_response(error: Exception, default_message: str = "服务暂时不可用") -> Dict[str, Any]:
        logger.error(f"Exception occurred: {type(error).__name__}: {str(error)}")
        
        if isinstance(error, AudioProcessingError):
            return {
                "success": False,
                "error_code": error.error_code,
                "message": "音频处理失败，请检查音频文件格式",
                "timestamp": None
            }
        elif isinstance(error, STTError):
            return {
                "success": False,
                "error_code": error.error_code,
                "message": "语音识别失败，请重新录制或上传音频",
                "timestamp": None
            }
        elif isinstance(error, TTSError):
            return {
                "success": False,
                "error_code": error.error_code,
                "message": "语音合成失败，请稍后重试",
                "timestamp": None
            }
        else:
            return {
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": default_message,
                "timestamp": None
            }

class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    """全局异常处理中间件"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            error_response = SafeExceptionHandler.get_safe_error_response(exc)
            
            if isinstance(exc, (AudioProcessingError, STTError, TTSError)):
                status_code = 422
            else:
                status_code = 500
                
            return JSONResponse(
                status_code=status_code,
                content=error_response
            )

def setup_exception_handlers(app):
    """设置异常处理器"""
    app.add_middleware(GlobalExceptionMiddleware)
    logger.info("全局异常处理中间件已注册")
