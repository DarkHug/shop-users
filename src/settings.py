from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class PasswordSettings(BaseModel):
    pepper: SecretStr
    hash_iterations: int


class DatabaseSettings(BaseModel):
    url: SecretStr


class SMTPSettings(BaseModel):
    server: str = "smtp.gmail.com"
    port: int = 587
    sender_email: str
    sender_password: str


class RabbitMQSettings(BaseModel):
    url: SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    # database
    db: DatabaseSettings

    smtp: SMTPSettings

    # rabbitmq
    rabbitmq: RabbitMQSettings

    password: PasswordSettings
