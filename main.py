from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from database import get_db
from models import User
from schemas import UserCreate, UserOut, Token
from auth import hash_password, create_jwt_token, verify_password, verify_jwt_token

app = FastAPI(
    title="Task Tracker API",
    description="Приложение для управления задачами. Пользователи, JWT и CRUD для задач.",
    version="1.0.0"
)

# регистрация
@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь с таким логином
    existing_user = db.query(User).filter(User.username == user.username).first() # первый найденный объект
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    # Хешируем пароль перед сохранением
    hashed_pw = hash_password(user.password)
    # Создаём нового пользователя
    new_user = User(
        username=user.username,
        hashed_password=hashed_pw
    )
    # Сохраняем его в базе
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # обновление БД
    # Возвращаем UserOut (id, username)
    return new_user


# вход
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # готовая форма авторизации ↑, автоматически принимает username и password
    # ищем пользователя в БД
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # Генерируем токен
    token = create_jwt_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}


# достаёт пользователя по JWT из заголовка
def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    if not authorization.startswith("Bearer "): # если заголовок неправильный
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1] # берем вторую часть строки, т.е. JWT
    payload = verify_jwt_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
