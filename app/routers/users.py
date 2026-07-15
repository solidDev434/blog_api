from fastapi import APIRouter, status

from core.dependency import CurrentUser
from schemas.users import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
async def read_users(user: CurrentUser):
    return user


@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
async def read_users(user: CurrentUser):
    print("user")
