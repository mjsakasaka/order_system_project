from pydantic import BaseModel
import os


class Settings(BaseModel):
    ENV: str = os.getenv("ENV", "dev")  # dev | test
    APP_NAME: str = os.getenv("APP_NAME", "oms-api")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # 建议用 SQLAlchemy URL（你后面会用到）
    # dev 默认连接 33061，test 默认连接 33062
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://oms:oms@127.0.0.1:33061/oms_dev?charset=utf8mb4",
    )
    DATABASE_URL_TEST: str = os.getenv(
        "DATABASE_URL_TEST",
        "mysql+pymysql://oms:oms@127.0.0.1:33062/oms_test?charset=utf8mb4",
    )

    TRACE_HEADER_NAME: str = os.getenv("TRACE_HEADER_NAME", "X-Trace-Id")


settings = Settings()


def get_database_url() -> str:
    """根据 ENV 返回对应 DB，确保 test 不污染 dev。"""
    if settings.ENV.lower() == "test":
        return settings.DATABASE_URL_TEST
    return settings.DATABASE_URL
