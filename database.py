# from sqlalchemy import create_engine
# # from sqlalchemy.ext.declarative import declarative_base
# # from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv
# from sqlalchemy.orm import sessionmaker, declarative_base
# import os
#
# load_dotenv()
#
# # SQLALCHEMY_DATABASE_URL = "sqlite:///./cafe_app.db"
# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
#
# # engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
#
# # Функція для отримання сесії бази даних
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Вказуємо шлях до файлу явно (про всяк випадок)
load_dotenv()

# 2. Отримуємо змінну
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 3. Додаємо ПЕРЕВІРКУ (якщо тут вилетить помилка, ми точно знатимемо чому)
if SQLALCHEMY_DATABASE_URL is None:
    # Це повідомлення підкаже нам, що саме не так
    print("--- КРИТИЧНА ПОМИЛКА ---")
    print("Змінна DATABASE_URL не знайдена!")
    print(f"Поточна робоча директорія: {os.getcwd()}")
    print("Файли в директорії:", os.listdir())
    raise ValueError("DATABASE_URL is None. Перевір файл .env")

# 4. Створюємо engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
