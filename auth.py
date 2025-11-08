#-------------- Логика безопасности + JWT --------------#

from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Создаём контекст хеширования, выбирая bcrypt из контейнера, deprecated - отмечать старые алгоритмы
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Функция для хеширования пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Функция для проверки пароля при входе
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Функция для cоздания JWT токена
def create_jwt_token(data: dict):
    to_encode = data.copy()  # создаём копию данных
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # добавляем время истечения токена
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Функция для проверки JWT токена
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # нагрузка. например, {"user_id": 1, "exp": ...}
    except jwt.ExpiredSignatureError:
        return None  # токен истёк
    except jwt.InvalidTokenError:
        return None  # токен неверен
