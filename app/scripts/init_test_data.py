import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.database import Base
from app.models.database import UserModel, Permissions, RoleEnum
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
                "role": RoleEnum.ADMIN,
                "is_active": True
            },
            {
                "name": "Менеджер",
                "surname": "Менеджеров",
                "email": "manager@example.com",
                "password": "manager123",
                "role": RoleEnum.MANAGER,
                "is_active": True
            },
            {
                "name": "Иван",
                "surname": "Иванов",
                "email": "user@example.com",
                "password": "user123",
                "role": RoleEnum.USER,
                "is_active": True
            },
            {
                "name": "Петр",
                "surname": "Петров",
                "email": "viewer@example.com",
                "password": "viewer123",
                "role": RoleEnum.VIEWER,
                "is_active": True
            },
            {
                "name": "Удаленный",
                "surname": "Пользователь",
                "email": "deleted@example.com",
                "password": "deleted123",
                "role": RoleEnum.USER,
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
            {"role": RoleEnum.ADMIN, "resource": "products", "action": "read", "allowed": True},
            {"role": RoleEnum.ADMIN, "resource": "products", "action": "create", "allowed": True},
            {"role": RoleEnum.ADMIN, "resource": "products", "action": "update", "allowed": True},
            {"role": RoleEnum.ADMIN, "resource": "products", "action": "delete", "allowed": True},
            {"role": RoleEnum.ADMIN, "resource": "orders", "action": "read", "allowed": True},
            {"role": RoleEnum.ADMIN, "resource": "orders", "action": "create", "allowed": True},
            {"role": RoleEnum.ADMIN, "resource": "orders", "action": "update", "allowed": True},
            {"role": RoleEnum.ADMIN, "resource": "orders", "action": "delete", "allowed": True},
            {"role": RoleEnum.ADMIN, "resource": "reports", "action": "read", "allowed": True},
            
            # Менеджер - может читать и создавать продукты, управлять заказами
            {"role": RoleEnum.MANAGER, "resource": "products", "action": "read", "allowed": True},
            {"role": RoleEnum.MANAGER, "resource": "products", "action": "create", "allowed": True},
            {"role": RoleEnum.MANAGER, "resource": "products", "action": "update", "allowed": True},
            {"role": RoleEnum.MANAGER, "resource": "products", "action": "delete", "allowed": False},
            {"role": RoleEnum.MANAGER, "resource": "orders", "action": "read", "allowed": True},
            {"role": RoleEnum.MANAGER, "resource": "orders", "action": "create", "allowed": True},
            {"role": RoleEnum.MANAGER, "resource": "orders", "action": "update", "allowed": True},
            {"role": RoleEnum.MANAGER, "resource": "orders", "action": "delete", "allowed": False},
            {"role": RoleEnum.MANAGER, "resource": "reports", "action": "read", "allowed": True},

            # Обычный пользователь - только чтение продуктов и создание заказов
            {"role": RoleEnum.USER, "resource": "products", "action": "read", "allowed": True},
            {"role": RoleEnum.USER, "resource": "products", "action": "create", "allowed": False},
            {"role": RoleEnum.USER, "resource": "products", "action": "update", "allowed": False},
            {"role": RoleEnum.USER, "resource": "products", "action": "delete", "allowed": False},
            {"role": RoleEnum.USER, "resource": "orders", "action": "read", "allowed": True},
            {"role": RoleEnum.USER, "resource": "orders", "action": "create", "allowed": True},
            {"role": RoleEnum.USER, "resource": "orders", "action": "update", "allowed": False},
            {"role": RoleEnum.USER, "resource": "orders", "action": "delete", "allowed": False},
            {"role": RoleEnum.USER, "resource": "reports", "action": "read", "allowed": False},
            
            # Читатель - только чтение
            {"role": RoleEnum.VIEWER, "resource": "products", "action": "read", "allowed": True},
            {"role": RoleEnum.VIEWER, "resource": "products", "action": "create", "allowed": False},
            {"role": RoleEnum.VIEWER, "resource": "products", "action": "update", "allowed": False},
            {"role": RoleEnum.VIEWER, "resource": "products", "action": "delete", "allowed": False},
            {"role": RoleEnum.VIEWER, "resource": "orders", "action": "read", "allowed": True},
            {"role": RoleEnum.VIEWER, "resource": "orders", "action": "create", "allowed": False},
            {"role": RoleEnum.VIEWER, "resource": "orders", "action": "update", "allowed": False},
            {"role": RoleEnum.VIEWER, "resource": "orders", "action": "delete", "allowed": False},
            {"role": RoleEnum.VIEWER, "resource": "reports", "action": "read", "allowed": False},
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
