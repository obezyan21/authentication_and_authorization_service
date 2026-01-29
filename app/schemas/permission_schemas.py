from pydantic import BaseModel
from app.schemas.user_schemas import RoleEnum


class PermissionCreateSchema(BaseModel):
    role: RoleEnum
    resource: str
    action: str
    allowed: bool = True


class PermissionUpdateSchema(BaseModel):
    allowed: bool


class PermissionResponseSchema(BaseModel):
    id: int
    role: str
    resource: str
    action: str
    allowed: bool

    class Config:
        from_attributes = True


class UserPermissionSchema(BaseModel):
    resource: str
    action: str
    allowed: bool

