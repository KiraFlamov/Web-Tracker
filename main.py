from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates

from database import get_db
from models import User, Task
from schemas import UserCreate, UserOut, Token, TaskOut, TaskCreate, TaskUpdate
from auth import hash_password, create_jwt_token, verify_password, verify_jwt_token

app = FastAPI(
    title="Task Tracker API",
    description="Приложение для управления задачами. Пользователи, JWT и CRUD для задач.",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates") # подключаем Jinja2

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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_jwt_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# информация о текущем юзере
@app.get("/users/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


# показать список задач текущего юзера
@app.get("/tasks", response_model=list[TaskOut])
def read_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks


# создать задачу
@app.post("/create_task", response_model=TaskOut)
def create_task(task: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        user_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


# изменить задачу
@app.put("/tasks/{task_id}", response_model=TaskOut)
def edit_task(task_id: int, task: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.title is not None:
        existing_task.title = task.title
    if task.description is not None:
        existing_task.description = task.description
    if task.status is not None:
        existing_task.status = task.status

    db.commit()
    db.refresh(existing_task)
    return existing_task


# удалить задачу
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return