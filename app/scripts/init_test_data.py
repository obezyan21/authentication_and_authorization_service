import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.database import Base
from app.models.database import UserModel, Permissions, UserRole
from app.core.security import get_password_hash


async def init_test_data():
    engine = create_async_engine("sqlite+aiosqlite:///auth.db")
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        users_query = select(UserModel)
        users_result = await session.execute(users_query)
        existing_users = users_result.scalars().all()
        
        if existing_users:
            print("В базе данных уже есть пользователи. Пропускаем инициализацию.")
            return
        
        test_users = [
            {
                "name": "Админ",
                "surname": "Админов",
                "email": "admin@example.com",
                "password": "admin123",
                "role": UserRole.ADMIN,
                "is_active": True
            },
            {
                "name": "Менеджер",
                "surname": "Менеджеров",
                "email": "manager@example.com",
                "password": "manager123",
                "role": UserRole.MANAGER,
                "is_active": True
            },
            {
                "name": "Иван",
                "surname": "Иванов",
                "email": "user@example.com",
                "password": "user123",
                "role": UserRole.USER,
                "is_active": True
            },
            {
                "name": "Петр",
                "surname": "Петров",
                "email": "viewer@example.com",
                "password": "viewer123",
                "role": UserRole.VIEWER,
                "is_active": True
            },
            {
                "name": "Удаленный",
                "surname": "Пользователь",
                "email": "deleted@example.com",
                "password": "deleted123",
                "role": UserRole.USER,
                "is_active": False
            }
        ]
        
        for user_data in test_users:
            user = UserModel(
                name=user_data["name"],
                surname=user_data["surname"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                is_active=user_data["is_active"]
            )
            session.add(user)
        
        await session.commit()
        
        test_permissions = [
            # Администратор - полный доступ ко всему
            {"role": UserRole.ADMIN, "resource": "products", "action": "read", "allowed": True},
            {"role": UserRole.ADMIN, "resource": "products", "action": "create", "allowed": True},
            {"role": UserRole.ADMIN, "resource": "products", "action": "update", "allowed": True},
            {"role": UserRole.ADMIN, "resource": "products", "action": "delete", "allowed": True},
            {"role": UserRole.ADMIN, "resource": "orders", "action": "read", "allowed": True},
            {"role": UserRole.ADMIN, "resource": "orders", "action": "create", "allowed": True},
            {"role": UserRole.ADMIN, "resource": "orders", "action": "update", "allowed": True},
            {"role": UserRole.ADMIN, "resource": "orders", "action": "delete", "allowed": True},
            {"role": UserRole.ADMIN, "resource": "reports", "action": "read", "allowed": True},
            
            # Менеджер - может читать и создавать продукты, управлять заказами
            {"role": UserRole.MANAGER, "resource": "products", "action": "read", "allowed": True},
            {"role": UserRole.MANAGER, "resource": "products", "action": "create", "allowed": True},
            {"role": UserRole.MANAGER, "resource": "products", "action": "update", "allowed": True},
            {"role": UserRole.MANAGER, "resource": "products", "action": "delete", "allowed": False},
            {"role": UserRole.MANAGER, "resource": "orders", "action": "read", "allowed": True},
            {"role": UserRole.MANAGER, "resource": "orders", "action": "create", "allowed": True},
            {"role": UserRole.MANAGER, "resource": "orders", "action": "update", "allowed": True},
            {"role": UserRole.MANAGER, "resource": "orders", "action": "delete", "allowed": False},
            {"role": UserRole.MANAGER, "resource": "reports", "action": "read", "allowed": True},
            
            # Обычный пользователь - только чтение продуктов и создание заказов
            {"role": UserRole.USER, "resource": "products", "action": "read", "allowed": True},
            {"role": UserRole.USER, "resource": "products", "action": "create", "allowed": False},
            {"role": UserRole.USER, "resource": "products", "action": "update", "allowed": False},
            {"role": UserRole.USER, "resource": "products", "action": "delete", "allowed": False},
            {"role": UserRole.USER, "resource": "orders", "action": "read", "allowed": True},
            {"role": UserRole.USER, "resource": "orders", "action": "create", "allowed": True},
            {"role": UserRole.USER, "resource": "orders", "action": "update", "allowed": False},
            {"role": UserRole.USER, "resource": "orders", "action": "delete", "allowed": False},
            {"role": UserRole.USER, "resource": "reports", "action": "read", "allowed": False},
            
            # Читатель - только чтение
            {"role": UserRole.VIEWER, "resource": "products", "action": "read", "allowed": True},
            {"role": UserRole.VIEWER, "resource": "products", "action": "create", "allowed": False},
            {"role": UserRole.VIEWER, "resource": "products", "action": "update", "allowed": False},
            {"role": UserRole.VIEWER, "resource": "products", "action": "delete", "allowed": False},
            {"role": UserRole.VIEWER, "resource": "orders", "action": "read", "allowed": True},
            {"role": UserRole.VIEWER, "resource": "orders", "action": "create", "allowed": False},
            {"role": UserRole.VIEWER, "resource": "orders", "action": "update", "allowed": False},
            {"role": UserRole.VIEWER, "resource": "orders", "action": "delete", "allowed": False},
            {"role": UserRole.VIEWER, "resource": "reports", "action": "read", "allowed": False},
        ]
        
        for perm_data in test_permissions:
            permission = Permissions(
                role=perm_data["role"],
                resource=perm_data["resource"],
                action=perm_data["action"],
                allowed=perm_data["allowed"]
            )
            session.add(permission)
        
        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_test_data())
