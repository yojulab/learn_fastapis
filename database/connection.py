import os
import psycopg2
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DB_HOST: Optional[str] = os.getenv("DB_HOST", "db_postgresql")
    DB_PORT: Optional[str] = os.getenv("DB_PORT", "5432")
    POSTGRES_DB: Optional[str] = os.getenv("POSTGRES_DB", "main_db")
    POSTGRES_USER: Optional[str] = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD: Optional[str] = os.getenv("POSTGRES_PASSWORD", "admin123")
    DATABASE_URL: Optional[str] = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"
    SECRET_KEY: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()

def get_db_connection():
    """PostgreSQL 데이터베이스에 연결하고 커서를 제공하는 제너레이터입니다."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD
        )
        yield conn
    finally:
        if conn:
            conn.close()
