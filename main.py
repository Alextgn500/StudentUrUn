from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from sqlalchemy import text

from app.db.database import get_db
from app.services.service_factory import (
    get_ticket_service,
    get_comment_service,
    get_user_service,
    get_analytic_service,
    get_sla_service,
)
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.schemas.tag import Tag
from app.services.sla_service import SLAService 
from app.api import auth
from app.core.config import settings
import logging


logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__) 

app = FastAPI(
    title="Tasks Management System API",
    description="API для системы управления задачами и тикетами",
    version="1.0.0"
)

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Tasks Management System API"}

@app.get("/check-db-with-logging")
def check_database_with_logging(db: Session = Depends(get_db)):
    try:
        logger.info("Attempting to connect to database...")
        result = db.execute(text("SELECT 1")).fetchone()
        logger.info(f"Database connection successful, result: {result}")
        return {"status": "success", "message": "Соединение с базой данных успешно установлено!"}
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return {"status": "error", "message": f"Ошибка подключения к базе данных: {str(e)}"}

@app.get("/check-db-connection")
def check_db_connection():
    try:
        # Прямое подключение без использования ORM
        from sqlalchemy import create_engine, text
        
        # Используем URL напрямую для тестирования
        test_url = "postgresql://postgres:000@localhost:5432/mydb"
        test_engine = create_engine(test_url)
        
        with test_engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            return {
                "status": "success",
                "message": "Прямое подключение к БД успешно",
                "result": result
            }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return {
            "status": "error",
            "message": f"Ошибка при прямом подключении: {str(e)}",
            "trace": error_trace
        }

@app.get("/db-info")
def db_info():
    try:
        # Прямое подключение без использования ORM
        from sqlalchemy import create_engine, text
        import psycopg2
        
        # Используем URL напрямую для тестирования
        test_url = "postgresql://postgres:000@localhost:5432/mydb"
        test_engine = create_engine(test_url)
        
        with test_engine.connect() as connection:
            # Получаем версию PostgreSQL
            pg_version = connection.execute(text("SELECT version()")).scalar()
            
            # Получаем информацию о psycopg2
            psycopg2_version = psycopg2.__version__
            
            # Проверяем кодировку
            client_encoding = connection.execute(text("SHOW client_encoding")).scalar()
            server_encoding = connection.execute(text("SHOW server_encoding")).scalar()
            
            return {
                "status": "success",
                "postgresql_version": pg_version,
                "psycopg2_version": psycopg2_version,
                "client_encoding": client_encoding,
                "server_encoding": server_encoding
            }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return {
            "status": "error",
            "message": f"Ошибка: {str(e)}",
            "trace": error_trace
        }

@app.get("/direct-psycopg2")
def direct_psycopg2():
    try:
        import psycopg2
        
        # Прямое подключение через psycopg2
        conn = psycopg2.connect(
            host="localhost",
            database="mydb",
            user="postgres",
            password="000",
            # Явно указываем кодировку
            options="-c client_encoding=utf8"
        )
        
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        
        # Проверяем кодировку
        cur.execute("SHOW client_encoding;")
        client_encoding = cur.fetchone()[0]
        
        cur.execute("SHOW server_encoding;")
        server_encoding = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return {
            "status": "success",
            "version": version,
            "client_encoding": client_encoding,
            "server_encoding": server_encoding
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return {
            "status": "error",
            "message": f"Ошибка при прямом подключении через psycopg2: {str(e)}",
            "trace": error_trace
        }


# Маршруты для тикетов
@app.get("/tickets/", response_model=List[TicketResponse], tags=["Тикеты"])
def read_tickets(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Получить список всех тикетов с возможностью фильтрации по статусу
    """
    ticket_service = get_ticket_service(db)
    tickets = ticket_service.get_tickets(skip=skip, limit=limit, status=status)
    return tickets


@app.get("/tickets/{ticket_id}", response_model=TicketResponse, tags=["Тикеты"])
def read_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """
    Получить детальную информацию о тикете по ID
    """
    ticket_service = get_ticket_service(db)
    ticket = ticket_service.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Тикет не найден")
    return ticket

@app.post("/tickets/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED, tags=["Тикеты"])
def create_ticket(ticket: TicketCreate, user_id: int = 1, db: Session = Depends(get_db)):
    """
    Создать новый тикет
    
    - **title**: название тикета
    - **description**: описание задачи/проблемы
    - **priority**: приоритет (low, medium, high, critical)
    - **client_id**: ID клиента
    """
    ticket_service = get_ticket_service(db)
    return ticket_service.create_ticket(ticket, created_by=user_id)

@app.put("/tickets/{ticket_id}", response_model=TicketResponse, tags=["Тикеты"])
def update_ticket(ticket_id: int, ticket: TicketUpdate, user_id: int = 1, db: Session = Depends(get_db)):
    """
    Обновить существующий тикет
    """
    ticket_service = get_ticket_service(db)
    db_ticket = ticket_service.get_ticket(ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Тикет не найден")
    
    updated_ticket = ticket_service.update_ticket(ticket_id, ticket, updated_by=user_id)
    return updated_ticket

@app.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Тикеты"])
def delete_ticket(ticket_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """
    Удалить тикет
    """
    ticket_service = get_ticket_service(db)
    db_ticket = ticket_service.get_ticket(ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Тикет не найден")
    
    ticket_service.delete_ticket(ticket_id, deleted_by=user_id)
    return None

@app.post("/tickets/{ticket_id}/assign", response_model=TicketResponse, tags=["Тикеты"])
def assign_ticket(ticket_id: int, assignee_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """
    Назначить тикет исполнителю
    """
    ticket_service = get_ticket_service(db)
    return ticket_service.assign_ticket(ticket_id, assignee_id, assigned_by=user_id)

@app.post("/tickets/{ticket_id}/comments/", response_model=CommentResponse, tags=["Комментарии"])
def add_comment(ticket_id: int, comment: CommentCreate, user_id: int = 1, db: Session = Depends(get_db)):
    """
    Добавить комментарий к тикету
    """
    ticket_service = get_ticket_service(db)
    return ticket_service.add_comment(ticket_id, comment, user_id=user_id)

@app.post("/tickets/{ticket_id}/tags/{tag_id}", response_model=TicketResponse, tags=["Теги"])
def add_tag_to_ticket(ticket_id: int, tag_id: int, db: Session = Depends(get_db)):
    """
    Добавить тег к тикету
    """
    ticket_service = get_ticket_service(db)
    return ticket_service.add_tag(ticket_id, tag_id)

@app.get("/tickets/report/by-status", tags=["Отчеты"])
def ticket_report_by_status(db: Session = Depends(get_db)):
    """
    Сформировать отчет по количеству тикетов в разных статусах
    """
    ticket_service = get_ticket_service(db)
    return ticket_service.get_tickets_report_by_status()

# Маршруты для комментов

@app.post("/tickets/{ticket_id}/comments/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED, tags=["Комментарии"])
def create_comment_for_ticket(
    ticket_id: int,
    comment_in: CommentCreate,
    user_id: int = 1,  # TODO: заменить на реальную аутентификацию и получать текущего пользователя
    db: Session = Depends(get_db)
):
    """
    Создать комментарий для тикета

    - ticket_id: ID тикета, к которому добавляется комментарий
    - comment_in: данные для создания комментария
    - user_id: ID пользователя, создающего комментарий
    """
    comment_service = get_comment_service(db)
    try:
        comment = comment_service.create_comment(comment_in, user_id, ticket_id)
        return comment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tickets/{ticket_id}/comments/", response_model=List[CommentResponse], tags=["Комментарии"])
def get_comments_by_ticket(
    ticket_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список комментариев по ID тикета

    - ticket_id: ID тикета
    - skip: количество пропускаемых комментариев (для пагинации)
    - limit: максимальное количество комментариев для выборки
    """
    comment_service = get_comment_service(db)
    comments = comment_service.get_comments_by_ticket(ticket_id, skip, limit)
    return comments


@app.get("/comments/{comment_id}", response_model=CommentResponse, tags=["Комментарии"])
def read_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить комментарий по ID

    - comment_id: ID комментария
    """
    comment_service = get_comment_service(db)
    comment = comment_service.get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return comment


@app.put("/comments/{comment_id}", response_model=CommentResponse, tags=["Комментарии"])
def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    user_id: int = 1,  # TODO: заменить на реальную аутентификацию
    db: Session = Depends(get_db)
):
    """
    Обновить комментарий по ID

    - comment_id: ID комментария для обновления
    - comment_in: новые данные комментария
    - user_id: ID пользователя, выполняющего обновление
    """
    comment_service = get_comment_service(db)
    try:
        updated_comment = comment_service.update_comment(comment_id, comment_in, user_id)
        return updated_comment
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


@app.delete("/comments/{comment_id}", response_model=CommentResponse, tags=["Комментарии"])
def delete_comment(
    comment_id: int,
    user_id: int = 1,  # TODO: заменить на реальную аутентификацию
    db: Session = Depends(get_db)
):
    """
    Удалить комментарий по ID

    - comment_id: ID комментария для удаления
    - user_id: ID пользователя, выполняющего удаление
    """
    comment_service = get_comment_service(db)
    try:
        deleted_comment = comment_service.delete_comment(comment_id, user_id)
        return deleted_comment
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

# Маршруты для пользователей
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Пользователи"])
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Создать нового пользователя

    - user_in: данные для создания пользователя (email, username, пароль и т.д.)
    """
    user_service = get_user_service(db)
    existing_user = user_service.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    
    existing_username = user_service.get_user_by_username(user_in.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    
    user = user_service.create_user(user_in)
    return user


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Пользователи"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Получить информацию о пользователе по ID

    - user_id: идентификатор пользователя
    """
    user_service = get_user_service(db)
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@app.get("/users/", response_model=List[UserResponse], tags=["Пользователи"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получить список пользователей с пагинацией

    - skip: количество пропускаемых пользователей (для пагинации)
    - limit: максимальное количество пользователей для выборки
    """
    user_service = get_user_service(db)
    users = user_service.get_users(skip=skip, limit=limit)
    return users


@app.put("/users/{user_id}", response_model=UserResponse, tags=["Пользователи"])
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    """
    Обновить данные пользователя по ID

    - user_id: идентификатор пользователя
    - user_in: новые данные пользователя
    """
    user_service = get_user_service(db)
    user = user_service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


# Пример эндпойнта аутентификации (если необходимо)
@app.post("/users/authenticate", response_model=UserResponse, tags=["Пользователи"])
def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    """
    Аутентификация пользователя по имени и паролю

    - username: имя пользователя
    - password: пароль пользователя
    """
    user_service = get_user_service(db)
    user = user_service.authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    return user


# Зависимость для сервиса аналитики
def analytic_service_dependency(db: Session = Depends(get_db)):
    return get_analytic_service(db)


# Блок маршрутов аналитики
@app.get("/analytic/tickets/count", response_model=int, tags=["Аналитика"])
def count_tickets(service = Depends(analytic_service_dependency)):
    """
    Количество всех тикетов
    """
    return service.count_tickets()


@app.get("/analytic/users/count", response_model=int, tags=["Аналитика"])
def count_users(service = Depends(analytic_service_dependency)):
    """
    Количество всех пользователей
    """
    return service.count_users()


@app.get("/analytic/tickets/status", response_model=Dict[str, int], tags=["Аналитика"])
def tickets_per_status(service = Depends(analytic_service_dependency)):
    """
    Количество тикетов по статусам
    """
    return service.tickets_per_status()


@app.get("/analytic/tickets/client", response_model=Dict[str, int], tags=["Аналитика"])
def tickets_per_client(service = Depends(analytic_service_dependency)):
    """
    Количество тикетов по клиентам
    """
    return service.tickets_per_client()


@app.get("/analytic/tickets/average_resolution_time", response_model=Optional[float], tags=["Аналитика"])
def average_resolution_time(service = Depends(analytic_service_dependency)):
    """
    Среднее время решения тикета (в часах)
    """
    avg_time = service.average_resolution_time()
    if avg_time is None:
        raise HTTPException(status_code=404, detail="Нет закрытых тикетов для расчёта времени решения")
    return avg_time


@app.get("/analytic/tickets/tag", response_model=Dict[str, int], tags=["Аналитика"])
def tickets_per_tag(service = Depends(analytic_service_dependency)):
    """
    Количество тикетов по тегам
    """
    return service.tickets_per_tag()


@app.get("/analytic/users/{user_id}/activity_count", response_model=int, tags=["Аналитика"])
def user_activity_count(user_id: int, service = Depends(analytic_service_dependency)):
    """
    Количество активности пользователя по user_id
    """
    return service.user_activity_count(user_id)


@app.get("/analytic/tickets/{ticket_id}/comments_count", response_model=int, tags=["Аналитика"])
def comments_per_ticket(ticket_id: int, service = Depends(analytic_service_dependency)):
    """
    Количество комментариев к тикету по ticket_id
    """
    return service.comments_per_ticket(ticket_id)

# Зависимость для SLA-сервиса
def get_sla_service(db: Session = Depends(get_db)):
    return SLAService(db)


# Блок маршрутов sla
@app.get("/sla/violations/count", response_model=int, tags=["SLA"])
def count_sla_violations(sla_service: SLAService = Depends(get_sla_service)):
    """
    Получить количество тикетов, закрытых с нарушением SLA

    Возвращает число тикетов, у которых время закрытия больше срока SLA (sla_deadline).
    """
    return sla_service.sla_violations_count()


@app.get("/sla/tickets/nearing_deadline", response_model=int, tags=["SLA"])
def tickets_nearing_sla_deadline(
    hours: Optional[int] = 24,
    sla_service: SLAService = Depends(get_sla_service)
):
    """
    Получить количество тикетов, срок SLA которых истекает в ближайшие `hours` часов.

    - hours: количество часов до истечения срока SLA (по умолчанию 24)
    - Возвращает число открытых тикетов, у которых срок SLA истекает в указанный период.
    """
    return sla_service.tickets_nearing_sla_deadline(hours=hours)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)