#-------------- Схемы Pydantic (регистрация + вход) --------------#

from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel): # модель для регистрации
    username: str
    password: str

class Token(BaseModel): # модель для токена при входе
    access_token: str
    token_type: str = "bearer" # (значение по умолчанию)

class UserOut(BaseModel): # модель для вывода инфы о юзере
    id: int
    username: str
    class Config:
        from_attributes = True # чтобы FastAPI преобразовал User в JSON


# Общая схема для задач
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"

class TaskCreate(TaskBase):
    pass  # используется для создания новой задачи с теми же полями

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class TaskOut(TaskBase): # для вывода
    id: int
    user_id: int
    class Config:
        from_attributes = True
