from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 初始化数据库
from db import init_db

success = init_db.init_db()
if not success:
    print("数据库初始化失败")
else:
    print("数据库初始化成功")

# 导入路由
from api.langgraph_routes import router as langgraph_router

app = FastAPI(
    title="Happy Partner - 儿童故事互动AI系统",
    description="基于LangGraph的故事创作和角色扮演系统",
    version="2.0.0",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(langgraph_router, prefix="/api")


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

    # 使用默认端口8001避免冲突
    port = 8001
    host = "127.0.0.1"  # 使用127.0.0.1替代0.0.0.0
    uvicorn.run(app, host=host, port=port)
