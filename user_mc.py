from fastapi import FastAPI, APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from typing import Annotated
from app.backend.db_depends import get_db
from app.models import User
from app.routers.user import router as user_router
from app.schemas import CreateUser, UpdateUser
from slugify import slugify
from app.backend.db import engine
from sqlalchemy import text


# Создаем экземпляр приложения
app = FastAPI(
    title="User API",  # название API
    description="API для управления пользователями",  # описание API
    version="1.0.0"  # версия API
)


router = APIRouter(prefix='/users', tags=['users'])


@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    # Получаем все записи из таблицы User
    users = db.scalars(select(User)).all()
    return users


@router.get('/{user_id}')
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    # Получаем пользователя по id
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")
    return user


@router.post('/create')
async def create_user(user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    # Создаем slug из username
    slug = slugify(user.username)

    # Создаем нового пользователя
    stmt = insert(User).values(
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        age=user.age,
        slug=slug
    )
    db.execute(stmt)
    db.commit()

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put('/update/{user_id}')
async def update_user(user_id: int, user: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    # Проверяем существование пользователя
    existing_user = db.scalar(select(User).where(User.id == user_id))
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    # Создаем словарь с непустыми значениями для обновления
    update_data = {k: v for k, v in user.model_dump().items() if v is not None}
    if 'username' in update_data:
        update_data['slug'] = slugify(update_data['username'])

    # Обновляем пользователя
    stmt = update(User).where(User.id == user_id).values(update_data)
    db.execute(stmt)
    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User update is successful!'
    }


@router.delete('/delete/{user_id}')
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    # Проверяем существование пользователя
    existing_user = db.scalar(select(User).where(User.id == user_id))
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    # Удаляем пользователя
    stmt = delete(User).where(User.id == user_id)
    db.execute(stmt)
    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User delete is successful!'
    }

# Временный код для проверки таблиц
with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    tables = result.fetchall()
    print("\nСозданные таблицы:", tables, "\n")

app.include_router(user_router)