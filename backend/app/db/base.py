from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0 style declarative base.
    所有 ORM model 都要继承这个 Base。
    """
    pass
