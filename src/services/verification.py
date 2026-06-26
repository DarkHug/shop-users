import pyotp
from sqlalchemy.ext.asyncio import AsyncSession
from src.repos.user_verification_repo import UserVerificationRepository


def generate_code() -> str:
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    current_code = totp.now()
    return current_code


class VerificationService:
    def __init__(self, user_verification_repo: UserVerificationRepository, session: AsyncSession):
        self.user_verification_repo = user_verification_repo
        self.session = session

    async def get_code(self, user_id: int) -> str:
        code = await self.user_verification_repo.get_user_code(user_id)
        return code

    async def write_code(self, user_id: int):
        code = generate_code()
        await self.user_verification_repo.create_code(code, user_id)

    async def verify_code(self, code: str, user_id: int) -> bool:
        actual_code = await self.get_code(user_id)
        if code != actual_code:
            return False
        return True

    async def revoke_code(self, user_id: int) -> bool:
        new_code = generate_code()
        try_to_update = await self.user_verification_repo.update_code(new_code, user_id)
        if try_to_update:
            return True
        return False
