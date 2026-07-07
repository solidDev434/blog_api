from fastapi import FastAPI, APIRouter, Depends
from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import EmailStr
from core.db import init_db
from core.dependency import get_db_session
from routers import users, auth
from services.auth import AuthService
from schemas.users import UserCreate, UserResponse


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


@app.post("/test", response_model=UserResponse)
async def test_service(email: EmailStr, db: AsyncSession = Depends(get_db_session)):
    user = await AuthService.get_user_by_email(db, email)
    print(user.model_dump())
    return user


@app.post("/create-user", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db_session)):
    user = await AuthService.create_user(db, user)
    print(user)
    return user
