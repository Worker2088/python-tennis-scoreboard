import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Загружаем переменные из .env в память системы
load_dotenv()

# 2. Достаем данные
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# 3. Экранируем пароль прямо здесь (автоматически!)
safe_password = urllib.parse.quote_plus(password)

# берем URL из Docker
# но проверим, передал ли он готовую строку целиком
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    # Если мы запускаем код локально (без Docker), собираем из .env
    user = os.getenv("DB_USER")
    # ... сборка через urllib.parse как в твоем коде ...
    DB_URL = f"mysql+pymysql://{user}:{safe_password}@{host}:{port}/{db_name}"

engine = create_engine(DB_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


