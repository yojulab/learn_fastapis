import psycopg2
from database.connection import get_db_connection

def create_tables():
    """데이터베이스에 테이블을 생성합니다."""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS "user" (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            manager VARCHAR(255),
            sellist1 VARCHAR(255),
            comment TEXT,
            editorContent TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS event (
            id SERIAL PRIMARY KEY,
            creator VARCHAR(255),
            title VARCHAR(255) NOT NULL,
            image VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            tags JSONB,
            location VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS todo (
            id SERIAL PRIMARY KEY,
            item VARCHAR(255) NOT NULL
        )
        """
    )
    conn = None
    try:
        # 데이터베이스 연결
        conn = next(get_db_connection())
        cur = conn.cursor()
        # 각 SQL 명령 실행
        for command in commands:
            cur.execute(command)
        # 변경사항 커밋
        conn.commit()
        cur.close()
        print("테이블이 성공적으로 생성되었습니다.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    create_tables()
