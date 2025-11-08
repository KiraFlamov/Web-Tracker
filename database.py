#-------------- Связь с базой данных (БД) --------------#

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


#                              user    password             name of DB
DATABASE_URL = "postgresql://postgres:mydatabase@localhost/task_tracker" # Адрес БД

engine = create_engine(DATABASE_URL) # Движок БД

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # "Фабрика" для создания сессий

Base = declarative_base() # Базовый класс для всех моделей (таблиц)

def get_db(): # всп. функция для связи с БД
    db = SessionLocal() # создаем сессию
    try:
        yield db # передаем в функцию маршрута
    finally:
        db.close() # по завершении закрываем сессию