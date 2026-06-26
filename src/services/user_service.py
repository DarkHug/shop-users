from sqlalchemy.ext.asyncio import AsyncSession

from src.repos.user_repo import UserRepository
from src.services.verification import VerificationService
from src.broker.publisher import email_sender


# from src.utility.email_sender import send_email


class UserService:
    def __init__(self, user_repository: UserRepository, session: AsyncSession,
                 verifications_service: VerificationService):
        self.user_repository = user_repository
        self.session = session
        self.verifications_service = verifications_service

    async def create_user(self, user_data: dict):
        exists = await self.user_repository.get_user_by_email(user_data['email'])
        if exists:
            raise ValueError(f"User with email {user_data['email']} already exists")

        password = user_data.pop('password')
        user_data['hashed_password'] = password + 'hash'

        new_user = await self.user_repository.create_user(user_data)
        await self.verifications_service.write_code(new_user.id)
        await email_sender({"email": user_data['email'], "code": await self.verifications_service.get_code(new_user.id)})
        await self.session.commit()
        return new_user

    async def get_user_by_id(self, user_id: int):
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} does not exist")
        return user

    async def get_id_by_email(self, email: str):
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} does not exist")
        return user.id

    async def verify_user(self, email: str, code: str):
        user_id = await self.get_id_by_email(email)
        result = await self.verifications_service.verify_code(code, user_id)
        if result:
            user = await self.user_repository.get_user_by_id(user_id)
            user.is_verified = True
            await self.session.commit()
            return user
        return None

    async def revoke_code(self, email: str):
        user_id = await self.get_id_by_email(email)
        if not user_id:
            raise ValueError(f"User with email {email} does not exist")
        await self.verifications_service.revoke_code(user_id=user_id)
        await self.session.commit()
