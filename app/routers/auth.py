from fastapi import APIRouter

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login")
async def login_user():
    return "LOGIN USER"


@router.post("/register")
async def register_user():
    return "REGISTER USER"


@router.post("/logout")
async def logout():
    return "LOGOUT USER"


@router.post("/refresh")
async def refresh():
    return "REFRESH TOKEN"
