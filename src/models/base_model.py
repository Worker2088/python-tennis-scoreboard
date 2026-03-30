"""
Модуль содержит базовый декларативный класс для моделей SQLAlchemy.

Инициализирует метаданные для всех связанных таблиц.
"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy в проекте.
    
    Содержит объект metadata, который хранит информацию о всех таблицах.
    """
    pass