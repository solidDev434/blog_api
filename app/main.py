from fastapi import FastAPI
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

app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
