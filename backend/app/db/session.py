from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from ..core.config import get_database_url, settings

# 这里用 settings.ENV 决定连 dev 还是 test
DATABASE_URL = get_database_url()

# SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db() -> Session:
    """
    FastAPI dependency:
    - 每个请求创建一个 session
    - 请求结束后关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def debug_db_info() -> dict:
    """
    仅用于开发阶段确认：当前 ENV 连接的是哪一个 DB。
    """
    return {
        "env": settings.ENV,
        "database_url": str(engine.url),
    }
