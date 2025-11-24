# Project Overview

This is a FastAPI web application that provides a RESTful API for managing users, events, and todos. It uses MongoDB as its database and Jinja2 for templating.

## Building and Running

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up environment variables:**
    Create a `.env` file in the root directory with the following variables:
    ```
    DATABASE_URL=mongodb://<user>:<password>@<host>:<port>/<database_name>
    SECRET_KEY=<your_secret_key>
    ```

3.  **Run the application:**
    ```bash
    uvicorn main:app --reload
    ```
    The application will be available at `http://127.0.0.1:8000`.

## Development Conventions

*   **Code Style:** The code follows the PEP 8 style guide.
*   **API Design:** The API is designed to be RESTful, with endpoints for creating, reading, updating, and deleting resources.
*   **Authentication:** User authentication is handled using JWT (JSON Web Tokens).
*   **Database:** The application uses MongoDB as its database, with the `beanie` ODM for interacting with the database.
*   **Templating:** The frontend is rendered using Jinja2 templates.
*   **Routers:** The application is organized into routers for different resources (users, events, todos, etc.).
*   **Models:** The data models are defined in the `models` directory.

## 프로젝트 구조

```
/apps/learn_fastapis/
├───auth/               # 인증 관련 로직 (JWT, 비밀번호 해싱 등)
├───database/           # 데이터베이스 연결 관리
├───models/             # 데이터 모델 (Pydantic 모델, Beanie ODM 문서)
├───routes/             # API 엔드포인트 (라우터) 정의
├───templates/          # 프론트엔드 Jinja2 템플릿
├───resources/          # CSS, 이미지 등 정적 파일
├───utils/              # 페이지네이션과 같은 유틸리티 함수
├───main.py             # 애플리케이션의 메인 진입점
├───requirements.txt    # Python 의존성 목록
└───.env                # 환경 변수 파일
```