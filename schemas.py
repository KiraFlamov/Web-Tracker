#-------------- Схемы Pydantic (регистрация + вход) --------------#

from pydantic import BaseModel

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
