from datetime import datetime, timezone
import enum

from sqlalchemy import Integer, String, Boolean, Enum, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.schemas.user_schemas import RoleEnum


def get_utc_now():
    return datetime.now(timezone.utc)

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    surname: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), default=RoleEnum.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate= lambda: datetime.now(timezone.utc))    


class Permissions(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum))
    resource: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(20))
    allowed: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("role", "resource", "action", name="uq_role_resource_action"),)
