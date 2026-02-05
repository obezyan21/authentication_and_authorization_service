from fastapi import HTTPException
from sqlalchemy import select

from app.models.database import UserModel, Permissions
from app.schemas.user_schemas import RoleEnum
from app.database import SessionDep


class PermissionService:
    def __init__(self, session: SessionDep):
        self.session = session

    async def check_permission(self, user_id: int, resource: str, action: str) -> bool:
        user_query = select(UserModel).where(UserModel.id == user_id)
        user_result = await self.session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(status_code=404, detail="Пользователь не найден или удален")
        
        permission_query = select(Permissions).where(
            Permissions.role == user.role,
            Permissions.resource == resource,
            Permissions.action == action
        )
        permission_result = await self.session.execute(permission_query)
        permission = permission_result.scalar_one_or_none()
        
        if not permission:
            raise HTTPException(status_code=404, detail="Разрешение не найдено")
        
        return permission.allowed

    async def get_user_permissions(self, user_id: int) -> list[dict]:
        user_query = select(UserModel).where(UserModel.id == user_id)
        user_result = await self.session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(status_code=404, detail="Пользователь не найден или удален")
        
        permissions_query = select(Permissions).where(
            Permissions.role == user.role,
            Permissions.allowed == True
        )
        permissions_result = await self.session.execute(permissions_query)
        permissions = permissions_result.scalars().all()
        
        return [
            {
                "resource": perm.resource,
                "action": perm.action,
                "allowed": perm.allowed
            }
            for perm in permissions
        ]

    async def get_all_permissions(self) -> list[dict]:
        query = select(Permissions)
        result = await self.session.execute(query)
        permissions = result.scalars().all()
        
        return [
            {
                "id": perm.id,
                "role": perm.role.value,
                "resource": perm.resource,
                "action": perm.action,
                "allowed": perm.allowed
            }
            for perm in permissions
        ]

    async def create_permission(self, role: RoleEnum, resource: str, action: str, allowed: bool = True) -> dict:
        existing_query = select(Permissions).where(
            Permissions.role == role,
            Permissions.resource == resource,
            Permissions.action == action
        )
        existing_result = await self.session.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail=f"Правило для роли {role.value}, ресурса {resource} и действия {action} уже существует"
            )
        
        new_permission = Permissions(
            role=role,
            resource=resource,
            action=action,
            allowed=allowed
        )
        self.session.add(new_permission)
        await self.session.commit()
        await self.session.refresh(new_permission)
        
        return {
            "id": new_permission.id,
            "role": new_permission.role.value,
            "resource": new_permission.resource,
            "action": new_permission.action,
            "allowed": new_permission.allowed
        }

    async def update_permission(self, permission_id: int, allowed: bool = None) -> dict:
        query = select(Permissions).where(Permissions.id == permission_id)
        result = await self.session.execute(query)
        permission = result.scalar_one_or_none()
        
        if not permission:
            raise HTTPException(status_code=404, detail="Правило доступа не найдено")
        
        if allowed is not None:
            permission.allowed = allowed
        
        await self.session.commit()
        await self.session.refresh(permission)
        
        return {
            "id": permission.id,
            "role": permission.role.value,
            "resource": permission.resource,
            "action": permission.action,
            "allowed": permission.allowed
        }

    async def delete_permission(self, permission_id: int) -> dict:
        query = select(Permissions).where(Permissions.id == permission_id)
        result = await self.session.execute(query)
        permission = result.scalar_one_or_none()
        
        if not permission:
            raise HTTPException(status_code=404, detail="Правило доступа не найдено")
        
        self.session.delete(permission)
        await self.session.commit()
        
        return {"message": "Правило доступа удалено"}

