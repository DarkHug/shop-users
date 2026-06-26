from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from src.dependencies.user_dependencies import get_user_service
from src.schemas.user import UserCreate, UserRead, UserVerification

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, service=Depends(get_user_service)) -> UserRead:
    try:
        return await service.create_user(user.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/verify", status_code=status.HTTP_202_ACCEPTED)
async def verify_user(user: UserVerification, service=Depends(get_user_service)) -> UserRead:
    user_to_verify = await service.verify_user(email=user.email, code=user.code)
    if user_to_verify is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user_to_verify


@router.put("/revoke-code", status_code=status.HTTP_202_ACCEPTED)
async def revoke_code(email: str, service=Depends(get_user_service)):
    return await service.revoke_code(email=email)
