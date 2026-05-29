from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import recruitment
from app.config import settings  # ✅ settings 对象已在 config.py 中实例化

app = FastAPI(
    title="UX 公众号招募机器人",
    description="基于 FastAPI + LLM 的微信公众号自动招募系统",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recruitment.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", tags=["健康检查"])
async def root() -> dict:
    return {
        "status": "ok",
        "message": "服务运行正常 🚀",
        "model": settings.model_name,  # 验证配置是否正常加载
    }


@app.get("/workbench", tags=["工作台"])
async def workbench() -> FileResponse:
    return FileResponse("app/static/workbench.html")
