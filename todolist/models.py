from datetime import datetime, timedelta, timezone

from flask_login import UserMixin
from sqlalchemy import Column, VARCHAR, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from base_model import Base, BaseModel
from db_interaction import engine


class User(BaseModel, UserMixin):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(length=20), nullable=False, unique=True)
    email = Column(VARCHAR(length=20), nullable=False, unique=True)
    password_hash = Column(String, nullable=False, unique=True)
    tasks = relationship("Task", back_populates="user")

    # Метод хеширует пароль для сохранения в базе данных
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Метод проверяет, соответствует ли введенный пользователем пароль тому,
    # который хранится в базе данных
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Метод возвращает True, если пользователь активен
    def is_active(self):
        return True

    # Метод возвращает True, если пользователь авторизован
    def is_authenticated(self):
        return True

    # Метод возвращает True, если пользователь анонимный
    def is_anonymous(self):
        return False


# Метод для получения дефолтного значения поля "срок выполнения"
def default_due_date():
    return datetime.now(timezone.utc) + timedelta(days=1)


class Task(BaseModel):
    __tablename__ = "task"

    title = Column(VARCHAR(length=100), nullable=False, unique=True)
    description = Column(String)
    category = Column(VARCHAR(length=30), nullable=False)
    due_date = Column(DateTime, nullable=False, default=default_due_date)
    status = Column(VARCHAR(length=10), nullable=False, default="new")
    attachment = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="tasks")


Base.metadata.create_all(engine)
