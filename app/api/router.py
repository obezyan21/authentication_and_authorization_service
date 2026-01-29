from fastapi import APIRouter, Depends, HTTPException, Response, Request

from app.database import DatabaseService
from app.schemas.user_schemas import UserSchema, LoginSchema, UpdateSchema
from app.schemas.permission_schemas import PermissionCreateSchema, PermissionUpdateSchema, PermissionResponseSchema, UserPermissionSchema
from app.services.users_service import UserService
from app.services.permission_service import PermissionService
from app.api.dependencies import get_current_user, require_admin, check_permission
from app.database import SessionDep
from app.services.dependencies import get_user_service, get_permission_service, get_db_service
from app.core.security import create_access_token


router = APIRouter()
@router.post("/db")
async def setup_db(db_service: DatabaseService = Depends(get_db_service)):
    return await db_service.setup_database()


@router.post("/register")
async def registre_user(data: UserSchema, user_service: UserService = Depends(get_user_service)):
    result = await user_service.register_user(data)
    return result


@router.post("/login")
async def login_user(data: LoginSchema, response: Response, user_service: UserService = Depends(get_user_service)):
    result = await user_service.login_user(data)
    if result is None:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    access_token = create_access_token({"sub": str(result.id)})
    response.set_cookie(key="user_access_token", value=access_token, httponly=True)
    return {"access_token": access_token}


@router.post("/logout")
async def logout_user(
    response: Response,
    request: Request,
    session: SessionDep
):
    user_id = await get_current_user(request, session)
    response.delete_cookie(key="user_access_token", httponly=True)
    return {"message": "Пользователь вышел из системы"}


@router.patch("/me")
async def update_user(
    data: UpdateSchema,
    request: Request,
    session: SessionDep,
    user_service: UserService = Depends(get_user_service)
):
    user_id = await get_current_user(request, session)
    result = await user_service.update_user(data, user_id)
    return result


@router.patch("/me/delete_user")
async def delete_user(
    response: Response,
    request: Request,
    session: SessionDep,
    user_service: UserService = Depends(get_user_service)
):
    user_id = await get_current_user(request, session)
    result = await user_service.delete_user(user_id)
    
    response.delete_cookie(
        key="user_access_token",
        httponly=True)

    return result


@router.get("/admin/permissions", response_model=list[PermissionResponseSchema])
async def get_all_permissions(
    request: Request,
    session: SessionDep,
    permission_service: PermissionService = Depends(get_permission_service)
):
    await require_admin(request, session)
    permissions = await permission_service.get_all_permissions()
    return permissions


@router.post("/admin/permissions", response_model=PermissionResponseSchema)
async def create_permission(
    data: PermissionCreateSchema,
    request: Request,
    session: SessionDep,
    permission_service: PermissionService = Depends(get_permission_service)
):
    await require_admin(request, session)
    permission = await permission_service.create_permission(
        role=data.role,
        resource=data.resource,
        action=data.action,
        allowed=data.allowed
    )
    return permission


@router.patch("/admin/permissions/{permission_id}", response_model=PermissionResponseSchema)
async def update_permission(
    permission_id: int,
    data: PermissionUpdateSchema,
    request: Request,
    session: SessionDep,
    permission_service: PermissionService = Depends(get_permission_service)
):
    await require_admin(request, session)
    permission = await permission_service.update_permission(
        permission_id=permission_id,
        allowed=data.allowed
    )
    return permission


@router.delete("/admin/permissions/{permission_id}")
async def delete_permission(
    permission_id: int,
    request: Request,
    session: SessionDep,
    permission_service: PermissionService = Depends(get_permission_service)
):
    await require_admin(request, session)
    result = await permission_service.delete_permission(permission_id)
    return result


@router.get("/me/permissions", response_model=list[UserPermissionSchema])
async def get_my_permissions(
    request: Request,
    session: SessionDep,
    permission_service: PermissionService = Depends(get_permission_service)
):
    user_id = await get_current_user(request, session)
    permissions = await permission_service.get_user_permissions(user_id)
    return permissions

# Mock-View для бизнес-объектов

@router.get("/products")
async def get_products(
    request: Request,
    session: SessionDep
):
    user_id = await check_permission("products", "read", request, session)
    
    mock_products = [
        {"id": 1, "name": "Ноутбук", "price": 50000, "category": "Электроника"},
        {"id": 2, "name": "Смартфон", "price": 25000, "category": "Электроника"},
        {"id": 3, "name": "Наушники", "price": 5000, "category": "Аксессуары"},
        {"id": 4, "name": "Клавиатура", "price": 3000, "category": "Периферия"},
        {"id": 5, "name": "Мышь", "price": 1500, "category": "Периферия"},
    ]
    
    return {"products": mock_products, "total": len(mock_products)}


@router.get("/products/{product_id}")
async def get_product(
    product_id: int,
    request: Request,
    session: SessionDep
):
    user_id = await check_permission("products", "read", request, session)
    
    mock_product = {
        "id": product_id,
        "name": f"Продукт {product_id}",
        "price": 10000 * product_id,
        "category": "Электроника",
        "description": f"Описание продукта {product_id}",
        "in_stock": True
    }
    
    return mock_product


@router.post("/products")
async def create_product(
    request: Request,
    session: SessionDep
):
    user_id = await check_permission("products", "create", request, session)
    
    return {
        "message": "Продукт создан (Mock)",
        "product_id": 999,
        "status": "success"
    }


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    request: Request,
    session: SessionDep
):
    user_id = await check_permission("products", "update", request, session)
    
    return {
        "message": f"Продукт {product_id} обновлен (Mock)",
        "product_id": product_id,
        "status": "success"
    }


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    request: Request,
    session: SessionDep
):
    user_id = await check_permission("products", "delete", request, session)
    
    return {
        "message": f"Продукт {product_id} удален (Mock)",
        "product_id": product_id,
        "status": "success"
    }


@router.get("/orders")
async def get_orders(
    request: Request,
    session: SessionDep
):
    user_id = await check_permission("orders", "read", request, session)
    
    mock_orders = [
        {"id": 1, "user_id": user_id, "total": 75000, "status": "completed"},
        {"id": 2, "user_id": user_id, "total": 30000, "status": "pending"},
        {"id": 3, "user_id": user_id, "total": 15000, "status": "processing"},
    ]
    
    return {"orders": mock_orders, "total": len(mock_orders)}


@router.get("/reports")
async def get_reports(
    request: Request,
    session: SessionDep
):
    user_id = await check_permission("reports", "read", request, session)
    
    mock_reports = [
        {"id": 1, "name": "Отчет по продажам", "period": "2024-01"},
        {"id": 2, "name": "Отчет по клиентам", "period": "2024-01"},
    ]
    
    return {"reports": mock_reports, "total": len(mock_reports)}
