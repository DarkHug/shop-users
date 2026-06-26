from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # database
    database_url: str

    # smtp
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str
    sender_password: str

    # rabbitmq
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"


settings = Settings()