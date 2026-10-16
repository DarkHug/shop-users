import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.users import User


class Provider(StrEnum):
    GOOGLE = 'google'
    GITHUB = 'github'


class OAuthAccount(Base):
    __tablename__ = "oauth_account"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"), index=True)
    provider: Mapped[Provider] = mapped_column(String(20))
    sub: Mapped[str] = mapped_column(String(255))

    __table_args__ = (UniqueConstraint('sub', 'provider', name='unique_sub_provider'),)
    user: Mapped["User"] = relationship("User", back_populates="oauth_accounts")
