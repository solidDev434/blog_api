from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from core.db import init_db
from routers import users, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting")
    await init_db()
    yield
    print("Server is shutting down")

app = FastAPI(
    title="Blog API",
    lifespan=lifespan,
    version="1.0.0"
)

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(users.router, prefix="/api/v1")
v1_router.include_router(auth.router, prefix="/api/v1")
