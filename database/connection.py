import os
import psycopg2
from sqlmodel import create_engine, SQLModel
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
engine = create_engine(settings.DATABASE_URL, echo=True)

def get_db_connection():
    """PostgreSQL 데이터베이스에 연결합니다."""
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD
        )
        print("PostgreSQL 데이터베이스에 성공적으로 연결되었습니다.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"데이터베이스 연결에 실패했습니다: {e}")
        print("연결 정보를 확인하거나 Docker 컨테이너가 실행 중인지 확인하세요.")
        return None

def initialize_database():
    """데이터베이스 테이블을 생성합니다."""
    SQLModel.metadata.create_all(engine)

if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        initialize_database()
        conn.close()
        print("\nPostgreSQL 데이터베이스 연결이 종료되었습니다.")
