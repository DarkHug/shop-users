from http import HTTPStatus

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException

from src.dtos.auth import TokenReturnDTO
from src.dtos.oauth import URLReturnDTO, RedirectDataDTO
from src.exceptions.oauth import OAuthStateInvalid, OAuthCodeExchangeError, OAuthValidationError, OAuthEmailNotVerified, \
    OAuthProviderUnavailable
from src.models.oauth import Provider as OAuthProvider
from src.services.oauth_service import OAuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth-oauth"],
    route_class=DishkaRoute,
)


@router.get("/{provider}/url", response_model=URLReturnDTO)
async def get_url(provider: OAuthProvider, service: FromDishka[OAuthService]):
    return await service.get_authorization_url(provider)


@router.post("/{provider}/callback", status_code=HTTPStatus.OK, response_model=TokenReturnDTO)
async def callback(provider: OAuthProvider, dto: RedirectDataDTO, service: FromDishka[OAuthService]):
    try:
        return await service.login(provider=provider, code=dto.code, state=dto.state)
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
            detail=f"{provider} is temporarily unavailable, try again later",
        )
