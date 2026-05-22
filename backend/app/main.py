"""FastAPI 应用入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.exceptions import AppException
from app.api.v1.router import v1_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    # await init_redis()  # MVP 不强制 Redis
    yield
    # Shutdown
    # await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    description="河大家教小程序后端 API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(v1_router)


# ---- 全局异常处理 ----

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=200 if exc.code < 2000 else 400,
        content={"code": exc.code, "message": exc.message, "data": exc.data},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 5000, "message": f"服务器内部错误: {str(exc)}", "data": None},
    )


# ---- 健康检查 ----

@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
