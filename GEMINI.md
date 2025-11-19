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
