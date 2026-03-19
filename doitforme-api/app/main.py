from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.response import success_response


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(settings.log_level)
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    lifespan=lifespan,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)
register_exception_handlers(app)
app.include_router(v1_router, prefix=settings.api_v1_prefix)


@app.get("/health", summary="Liveness probe")
async def health() -> JSONResponse:
    payload, status_code = success_response({"status": "ok"})
    return JSONResponse(status_code=status_code, content=payload)


@app.get("/ready", summary="Readiness probe")
async def ready() -> JSONResponse:
    payload, status_code = success_response({"status": "ready"})
    return JSONResponse(status_code=status_code, content=payload)
