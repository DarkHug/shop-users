import uuid
from http import HTTPStatus
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.exceptions.auth import AccessTokenExpired, AccessTokenInvalid
from src.services.jwt_service import JWTService

security = HTTPBearer()


@inject
def get_current_user_id(
        service: FromDishka[JWTService],
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
