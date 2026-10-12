import datetime
import uuid

from pydantic import BaseModel


class RefreshTokenCreateDBDTO(BaseModel):
    user_id: uuid.UUID
    token_hash: str
    expires_at: datetime.datetime


class TokenReturnDTO(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenRequestDTO(BaseModel):
    refresh_token: str
