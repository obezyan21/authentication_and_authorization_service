from fastapi import HTTPException
from sqlalchemy import select, update, func

from app.models.database import UserModel
from app.core.security import verify_password, get_password_hash
from app.database import SessionDep
from app.schemas.user_schemas import UserSchema, LoginSchema, ResponseSchema, UpdateSchema


class UserService:
    def __init__(self, session: SessionDep):
        self.session = session

    async def register_user(self, data: UserSchema) -> dict:
        query = select(UserModel).where(UserModel.email == data.email)
        user = await self.session.execute(query)
        if user.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Такой пользователь уже существует")

        if data.password != data.password_confirm:
            raise HTTPException(status_code=400, detail="Пароли не совпадают")

        new_user = UserModel(
            name=data.name,
            surname=data.surname,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            role=data.role,
            is_active=True
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return {
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role,
            "is_active": new_user.is_active
        }

    async def login_user(self, data: LoginSchema) -> dict:
        query = select(UserModel).where(UserModel.email == data.email)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
    
        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Не правильный логин или пароль")
    
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Пользователь неактивен")
        
        return ResponseSchema.model_validate(user)

    async def update_user(self, data: UpdateSchema, user_id: int) -> dict:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Пользователь неактивен")

        update_data = data.model_dump(exclude_unset=True)
        query = update(UserModel).where(UserModel.id == user_id).values(**update_data)
        try:
            await self.session.execute(query)
            await self.session.commit()
            return {"message": "Данные изменены"}
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Изменение не удалось: {str(e)}")

    async def delete_user(self, user_id: int) -> dict:
        query = select(UserModel).where(UserModel.id == user_id, UserModel.is_active==True)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(404, "Пользователь не найден или уже удален")
        
        try:
            user.is_active = False
            user.updated_at = func.now()
            await self.session.commit()

            return {"message": "Пользователь удален", "email": user.email}
        
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении: {str(e)}")
