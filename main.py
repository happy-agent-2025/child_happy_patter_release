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

# 导入路由
from api.routes import router

app = FastAPI(title="Happy Partner - 儿童教育AI系统", 
              description="一个多代理架构的儿童教育AI系统，专注于教育辅助和情感陪伴",
              version="0.1.0")

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

@app.get("/")
async def root():
    return {"message": "Welcome to Happy Partner - 儿童教育AI系统"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)