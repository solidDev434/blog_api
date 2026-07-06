from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/")
async def read_users():
    return [{"user": "josephibok36@gmail.com"}]
