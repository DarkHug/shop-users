import uuid
from http import HTTPStatus
from typing import Annotated

from dishka.integrations.fastapi import FromDishka, DishkaRoute
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from src.dependencies import get_current_user_id
from src.dtos.auth import TokenReturnDTO, RefreshTokenRequestDTO
from src.dtos.users import UserCreateDTO, UserReadDTO, UserLoginDTO
from src.exceptions.auth import RefreshTokenExpired, RefreshTokenReused, RefreshTokenNotFound
from src.exceptions.users import EmailAlreadyExistsException, UsernameAlreadyExistsException, EmailNotFoundException
from src.exceptions.users import InvalidCredentialsException, UserNotFoundException
from src.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    route_class=DishkaRoute,
)


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_user(dto: UserCreateDTO, service: FromDishka[UserService]):
    try:
        await service.create(dto)
    except (EmailAlreadyExistsException, UsernameAlreadyExistsException) as e:

        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=e.message,
        )


@router.get("/", status_code=HTTPStatus.OK, response_model=UserReadDTO)
async def get_user_by_email(email: str, service: FromDishka[UserService]):
    try:
        return await service.get_by_email(email=email)
    except EmailNotFoundException as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=e.message,
        )


@router.post("/login", status_code=HTTPStatus.OK, response_model=TokenReturnDTO)
async def login(dto: UserLoginDTO, service: FromDishka[UserService]):
    try:
        return await service.login(email=dto.email, password=dto.password)
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=e.message,
        )


@router.get("/me", response_model=UserReadDTO)
async def get_me(service: FromDishka[UserService], user_id: Annotated[uuid.UUID, Depends(get_current_user_id)]):
    try:
        return await service.get_by_id(user_id)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=e.message,
        )


@router.post("/refresh", response_model=TokenReturnDTO)
async def refresh(service: FromDishka[UserService], dto: RefreshTokenRequestDTO):
    try:
        return await service.refresh_tokens(dto.refresh_token)
    except (RefreshTokenReused, RefreshTokenNotFound, RefreshTokenExpired) as e:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=e.message,
        )


@router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def logout(service: FromDishka[UserService], dto: RefreshTokenRequestDTO):
    try:
        return await service.logout(dto.refresh_token)
    except RefreshTokenNotFound as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=e.message,
        )
