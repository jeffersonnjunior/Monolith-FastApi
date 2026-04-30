from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AppUser


class AppUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> AppUser | None:
        result = await self._session.execute(select(AppUser).where(AppUser.email == email))
        return result.scalar_one_or_none()
