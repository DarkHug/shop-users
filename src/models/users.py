import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.refresh_token import RefreshToken


if TYPE_CHECKING:
    from src.models.oauth import OAuthAccount

class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_salt: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_code: Mapped["UserCodeVerifications"] = relationship(
        back_populates="user"
    )
    refresh_token: Mapped[list[RefreshToken]] = relationship(
        back_populates="user"
    )
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(back_populates="user")


class UserCodeVerifications(Base):
    __tablename__ = 'user_code_verifications'

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10))
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
    )
    user: Mapped["User"] = relationship(back_populates="verification_code")
