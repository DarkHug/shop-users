from sqlalchemy.orm import Mapped, mapped_column, validates, relationship
from sqlalchemy import String, Boolean, ForeignKey

from src.database.base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_code: Mapped["UserCodeVerifications"] = relationship(
        back_populates="user"
    )

    @validates("email")
    def validate_email(self, key, value):
        if '@' not in value:
            raise ValueError("Email address is not valid")
        return value.strip().lower()


class UserCodeVerifications(Base):
    __tablename__ = 'user_code_verifications'

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True
    )
    user: Mapped["User"] = relationship(back_populates="verification_code")