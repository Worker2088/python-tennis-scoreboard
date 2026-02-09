from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    # Этот класс пустой, но внутри него "под капотом"
    # живет объект metadata — коллекция всех наших таблиц.
    pass