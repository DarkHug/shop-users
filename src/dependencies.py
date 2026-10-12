import uuid
from http import HTTPStatus
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.services.user_service import UserService
from src.exceptions.auth import AccessTokenExpired, AccessTokenInvalid

security = HTTPBearer()


@inject
def get_current_user_id(
        service: FromDishka[UserService],
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> uuid.UUID:
    token = credentials.credentials
    try:
        res = service.verify_access_token(token)
    except (AccessTokenExpired, AccessTokenInvalid) as e:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return res
