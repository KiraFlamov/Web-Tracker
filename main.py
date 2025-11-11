from fastapi import FastAPI, Depends, HTTPException, Request, Form
from flask import request
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse

from database import get_db
from models import User, Task
from schemas import UserCreate, UserOut, Token, TaskOut, TaskCreate, TaskUpdate
from auth import hash_password, create_jwt_token, verify_password, verify_jwt_token

app = FastAPI()

templates = Jinja2Templates(directory="templates") # подключаем Jinja2


# достаёт пользователя по JWT из заголовка
def get_current_user(request: Request, db: Session = Depends(get_db)):
    # проверяем наличие токена, иначе возвращаем на логин
    if "access_token" in request.cookies:
        token = request.cookies.get("access_token")[7:]  # убираем "Bearer "
    if not token:
        return RedirectResponse("/login", status_code=303)

    # проверяем подлинность токена
    payload = verify_jwt_token(token)
    if payload is None:
        return RedirectResponse("/login", status_code=303)

    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if user is None:
        return RedirectResponse("/login", status_code=303)
    return user


# регистрация
@app.post("/register", response_class=HTMLResponse)
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
@app.post("/login")
def login(response: RedirectResponse, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # ищем пользователя в БД
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный логин или пароль"})

    # Генерируем токен
    token = create_jwt_token({"user_id": user.id})

    # возвращаем редирект на главную страницу + ставим cookie
    response = RedirectResponse(url="/home", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True) # httponly - чтобы никто не увидел
    return response





# информация о текущем юзере
@app.get("/users/me")
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