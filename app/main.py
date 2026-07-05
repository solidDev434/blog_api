from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.db import init_db


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


@app.get("/")
async def read_root():
    return {"Hello": "World"}
