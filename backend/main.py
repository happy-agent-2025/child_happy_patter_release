from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
from api.routes import router
from api.langgraph_routes import router as langgraph_router

app = FastAPI(
    title="Happy Partner - 儿童教育AI系统",
    description="一个多代理架构的儿童教育AI系统，专注于教育辅助和情感陪伴 - 支持LangGraph工作流",
    version="0.2.0",
    openapi_url="/openapi.json",
    docs_url=None,
    redoc_url=None
)

# 设置全局异常处理
setup_exception_handlers(app)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(router, prefix="/api")
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
    return {"message": "儿童教育AI系统API服务"}

if __name__ == "__main__":
    import uvicorn
    port = 8001
    host = "127.0.0.1"
    uvicorn.run(app, host=host, port=port)
