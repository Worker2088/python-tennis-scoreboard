import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine

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

# 4. Собираем URL
DB_URL = f"mysql+pymysql://{user}:{safe_password}@{host}:{port}/{db_name}"

engine = create_engine(DB_URL)