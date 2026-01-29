from app.database import SessionDep
from app.services.users_service import UserService
from app.services.permission_service import PermissionService
from app.database import DatabaseService

def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)

def get_permission_service(session: SessionDep) -> PermissionService:
    return PermissionService(session)

def get_db_service() -> DatabaseService:
    return DatabaseService()
