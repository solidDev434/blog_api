import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.db import init_db
from core.redis import redis_client
from routers import users, auth

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server is starting")
    await init_db()
    await redis_client.connect()

    yield
    logger.info("Server is shutting down")
    await redis_client.disconnect()

app = FastAPI(
    title="Blog API",
    lifespan=lifespan,
    version="1.0.0"
)

app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
