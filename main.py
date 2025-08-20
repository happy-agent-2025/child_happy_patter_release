from fastapi import FastAPI

app = FastAPI(
    title="Happy Partner - 儿童教育AI系统",
    description="一个多代理架构的儿童教育AI系统，专注于教育辅助和情感陪伴",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to Happy Partner - 儿童教育AI系统"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)