from fastapi import FastAPI, Depends, Request, Form, Query
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse

from database import get_db
from models import User, Task
from auth import hash_password, create_jwt_token, verify_password, verify_jwt_token

app = FastAPI()

templates = Jinja2Templates(directory="templates") # подключаем Jinja2


# -----------------------------
# Вспомогательная функция: текущий пользователь
# -----------------------------
def get_current_user(request: Request, db: Session = Depends(get_db)):
    # проверяем токен, при любой ошибке возвращаем на /login
    try:
        raw_token = request.cookies.get("access_token")
        if not raw_token or not raw_token.startswith("Bearer "):
            return None
        token = raw_token[7:]# убираем "Bearer "
        # проверяем подлинность токена
        payload = verify_jwt_token(token)
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        return user
    except Exception:
        return None


# ДЕКОРАТОРЫ

# --------------------------
# Регистрация
# --------------------------
@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь с таким логином
    existing_user = db.query(User).filter(User.username == username).first() # первый найденный объект
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пользователь уже существует!"})
    # Хешируем пароль перед сохранением
    hashed_pw = hash_password(password)
    # Создаём нового пользователя
    new_user = User(
        username=username,
        hashed_password=hashed_pw
    )
    # Сохраняем его в базе
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # обновление БД
    return RedirectResponse(url="/login", status_code=302)


# --------------------------
# Логин
# --------------------------
@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # ищем пользователя в БД
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный логин или пароль"})

    # Генерируем токен
    token = create_jwt_token({"user_id": user.id})

    # возвращаем редирект на главную страницу + ставим cookie с токеном
    response = RedirectResponse(url="/home", status_code=302)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True) # httponly - чтобы никто не увидел
    return response


# -----------------------------
# Logout
# -----------------------------
@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


# -----------------------------
# Редирект при главной вкладке /
# -----------------------------
@app.get("/")
def home():
    return RedirectResponse(url="/home", status_code=302)



# -----------------------------
# Список задач (home)
# -----------------------------
@app.get("/home", response_class=HTMLResponse)
def home_tasks(
        request: Request,
        sort: str = Query("date"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    query = db.query(Task).filter(Task.user_id == current_user.id)

    if sort == "status":
        # невыполненные сверху, выполненные снизу
        query = query.order_by(Task.status.asc())
    else:
        # по дате создания (новые сверху)
        query = query.order_by(Task.created_at.desc())

    tasks = query.all()

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "tasks": tasks,
            "user": current_user,
            "sort": sort
        }
    )



# -----------------------------
# Информация о пользователе
# -----------------------------
@app.get("/users/me", response_class=HTMLResponse)
def users_me(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("users_me.html", {"request": request, "user": current_user})




# -----------------------------
# Создать задачу
# -----------------------------
@app.post("/create_task")
def create_task(
        request: Request,
        title: str = Form(...),
        description: str = Form(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    new_task = Task(
        title=title,
        description=description,
        status="pending",  # 👈 статус задаётся сервером
        user_id=current_user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return RedirectResponse("/home", status_code=302)



# -----------------------------
# Изменить задачу
# -----------------------------
@app.post("/tasks/edit/{task_id}")
def edit_task(
        request: Request,
        task_id: int,
        title: str = Form(),
        description: str = Form(),
        status: str = Form(),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    existing_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not existing_task:
        return templates.TemplateResponse("home.html", {"request": request, "error": "Заметка не найдена"})

    if title is not None:
        existing_task.title = title
    if description is not None:
        existing_task.description = description
    if status is not None:
        existing_task.status = status

    db.commit()
    db.refresh(existing_task)
    return RedirectResponse(url="/home", status_code=302)


# -----------------------------
# Удалить задачу
# -----------------------------
@app.post("/tasks/delete/{task_id}")
def delete_task(
        request: Request,
        task_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        return templates.TemplateResponse("home.html", {"request": request, "error": "Заметка не найдена"})
    db.delete(task)
    db.commit()
    return RedirectResponse(url="/home", status_code=302)

# -----------------------------
# Изменить статус задачи
# -----------------------------
@app.post("/tasks/toggle/{task_id}")
def toggle_task_status(
        task_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        return RedirectResponse("/home", status_code=302)

    # переключаем статус
    task.status = "done" if task.status == "pending" else "pending"

    db.commit()
    return RedirectResponse("/home", status_code=302)
