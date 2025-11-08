#-------------- Подтянуть значения ключа из переменной среды --------------#

from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

# Читаем значения
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))