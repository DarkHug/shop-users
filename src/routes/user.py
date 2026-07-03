from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from src.dependencies.user_dependencies import get_user_service
from src.dtos.users import UserCreateDTO, UserReadDTO
from src.exceptions.user_exceptions import DuplicateFieldError, EntityNotFoundError

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(dto: UserCreateDTO, service=Depends(get_user_service)):
    try:
        await service.create(dto)
    except DuplicateFieldError as e:

        raise HTTPException(
            status_code=409,
            detail=str(e),
        )


@router.get("/", status_code=status.HTTP_200_OK, response_model=UserReadDTO)
async def get_user_by_email(email: str, service=Depends(get_user_service)):
    try:
        return await service.get_by_email(email=email)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
