#-------------- Связь с базой данных (БД) --------------#

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Адрес БД берём из переменной среды (на Render), иначе - локальная БД
#                                                      user    password             name of DB
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:mydatabase@localhost/task_tracker")
if DATABASE_URL.startswith("postgres://"): # SQLAlchemy понимает только "postgresql://"
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL) # Движок БД

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # "Фабрика" для создания сессий

Base = declarative_base() # Базовый класс для всех моделей (таблиц)

def get_db(): # всп. функция для связи с БД
    db = SessionLocal() # создаем сессию
    try:
        yield db # передаем в функцию маршрута
    finally:
        db.close() # по завершении закрываем сессию