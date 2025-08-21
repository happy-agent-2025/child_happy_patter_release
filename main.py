from fastapi import FastAPI
import sys
import os

# 将当前目录添加到Python路径中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 使用绝对导入而不是相对导入
from api.routes import router as api_router

app = FastAPI(
    title="Happy Partner - 儿童教育AI系统",
    description="一个多代理架构的儿童教育AI系统，专注于教育辅助和情感陪伴",
    version="0.1.0"
)

# 包含API路由
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Happy Partner - 儿童教育AI系统"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)