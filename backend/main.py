from fastapi import FastAPI
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
from db import init_db

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


if __name__ == "__main__":
    import uvicorn

    # 使用配置中的服务器设置
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )
