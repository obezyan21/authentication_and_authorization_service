import enum
from datetime import datetime

from pydantic import BaseModel, EmailStr


class RoleEnum(str, enum.Enum):
    ADMIN = "Администратор"
    MANAGER = "Менеджер"
    USER = "Пользователь"
    VIEWER = "Читатель"

class UserSchema(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    password_confirm: str
    role: RoleEnum = RoleEnum.USER

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class ResponseSchema(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    role: RoleEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UpdateSchema(BaseModel):
    name: str
    surname: str
    email: EmailStr
