from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from dishka.integrations.fastapi import FromDishka, inject, DishkaRoute
from src.dtos.users import UserCreateDTO, UserReadDTO
from src.exceptions.users import EmailAlreadyExistsException, UsernameAlreadyExistsException, EmailNotFoundException
from src.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    route_class=DishkaRoute,
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(dto: UserCreateDTO, service: FromDishka[UserService]):
    try:
        await service.create(dto)
    except (EmailAlreadyExistsException, UsernameAlreadyExistsException) as e:

        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=e.message,
        )


@router.get("/", status_code=status.HTTP_200_OK, response_model=UserReadDTO)
async def get_user_by_email(email: str, service: FromDishka[UserService]):
    try:
        return await service.get_by_email(email=email)
    except EmailNotFoundException as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=e.message,
        )
