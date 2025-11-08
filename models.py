#-------------- Описание моделей (таблиц) БД --------------#

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users" # имя таблицы БД

    id = Column(Integer, primary_key=True, index=True) # primary_key - уникальный id, index=True - индекс для быстрого поиска
    username = Column(String, unique=True, index=True) # unique - запретить повторение
    hashed_password = Column(String)

    tasks = relationship("Task", back_populates="owner") # связь полем "owner" в модели "Task"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String, default="pending")
    user_id = Column(Integer, ForeignKey("users.id")) # связь с id модели "User"

    owner = relationship("User", back_populates="tasks")