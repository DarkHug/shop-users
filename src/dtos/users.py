import re
import uuid

from pydantic import BaseModel, field_validator, EmailStr
from src.models.oauth import Provider

class UserCreateDTO(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        if len(value) < 3:
            raise ValueError("Имя пользователя должнно быть более 3 символов")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        if len(value) < 8:
            raise ValueError("Пароль должен быть более 8 символов")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r"[a-z]", value):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not re.search(r"[0-9]", value):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ")
        return value


class UserCreateDBDTO(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    password_salt: str


class UserOAuthCreateDBDTO(BaseModel):
    email: EmailStr
    is_verified: bool = True


class OAuthAccountCreateDBDTO(BaseModel):
    sub: str
    provider: Provider
    user_id: uuid.UUID


class UserReadDTO(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    is_verified: bool


class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str
