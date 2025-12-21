from datetime import datetime, timezone

from fastapi import Request, HTTPException
from sqlalchemy import select

from app.database import SessionDep
from app.core.security import verify_token
from app.models.database import UserModel, UserRole
from app.services.premission_service import PermissionService

async def get_current_user(request: Request, session: SessionDep) -> int:
    token = request.cookies.get("user_access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Токен не найден")

    payload = verify_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    expire = payload.get("exp")
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(status_code=401, detail="Токен истек")
    
    user_id_int = int(user_id)
    
    user_query = select(UserModel).where(UserModel.id == user_id_int)
    user_result = await session.execute(user_query)
    user = user_result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь неактивен")
    
    return user_id_int


async def get_current_user_with_role(request: Request, session: SessionDep) -> tuple[int, UserRole]:
    user_id = await get_current_user(request, session)
    
    user_query = select(UserModel).where(UserModel.id == user_id)
    user_result = await session.execute(user_query)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    return user_id, user.role


async def require_admin(request: Request, session: SessionDep) -> int:
    user_id, role = await get_current_user_with_role(request, session)
    
    if role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Доступ запрещен. Требуется роль администратора"
        )
    
    return user_id


async def check_permission(resource: str, action: str, request: Request, session: SessionDep) -> int:
    user_id = await get_current_user(request, session)
    permission_service = PermissionService(session)
    has_permission = await permission_service.check_permission(
        user_id, resource, action
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail=f"Доступ запрещен. Недостаточно прав для выполнения действия: {action}, источник: {resource}"
        )
    
    return user_id
