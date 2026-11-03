from http import HTTPStatus

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException

from src.exceptions.oauth import OAuthStateInvalid, OAuthCodeExchangeError, OAuthValidationError, OAuthEmailNotVerified, \
    OAuthProviderUnavailable
from src.dtos.auth import TokenReturnDTO
from src.dtos.oauth import URLReturnDTO, RedirectDataDTO
from src.services.google_auth_service import GoogleAuthService

router = APIRouter(
    prefix="/auth/google",
    tags=["auth-google"],
    route_class=DishkaRoute,
)


@router.get("/url", response_model=URLReturnDTO)
async def get_url(service: FromDishka[GoogleAuthService]):
    return await service.get_authorization_url()


@router.post("/callback", status_code=HTTPStatus.OK, response_model=TokenReturnDTO)
async def callback(dto: RedirectDataDTO, service: FromDishka[GoogleAuthService]):
    try:
        return await service.login(code=dto.code, state=dto.state)
    except (OAuthStateInvalid, OAuthCodeExchangeError, OAuthValidationError):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Session is expired, please try again",
        )
    except OAuthEmailNotVerified as e:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=e.message,
        )
    except OAuthProviderUnavailable:
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail="Google is temporarily unavailable, try again later",
        )
