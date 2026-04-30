from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
    )
