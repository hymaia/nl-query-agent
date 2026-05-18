from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import health, query
from app.config import settings
from app.logger import logger, setup_uvicorn_json_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_uvicorn_json_logging()
    logger.info(
        "application starting",
        extra={
            "env": settings.app_env,
            "bedrock_model_id": settings.bedrock_model_id,
            "glue_database": settings.glue_database,
            "aws_region": settings.aws_region,
        },
    )
    yield
    logger.info("application shutting down")


app = FastAPI(
    title="NL SQL Agent",
    description="Natural Language Query Agent — FastAPI + Bedrock Claude Sonnet + LangGraph",
    version="0.1.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url="/redoc" if settings.app_env != "production" else None,
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(health.router)
app.include_router(query.router, prefix="/api/v1")
