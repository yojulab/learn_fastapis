import psycopg2
from psycopg2.extras import DictCursor
from fastapi import APIRouter, Path, HTTPException, status, Request, Depends
from fastapi.templating import Jinja2Templates
from models.todos import Todo, TodoItem, TodoItems
from database.connection import get_db_connection

router = APIRouter(
    tags=["Todos"]
)

templates = Jinja2Templates(directory="templates/")

@router.post("/")
def add_todo(request: Request, todo: Todo = Depends(Todo.as_form), conn=Depends(get_db_connection)):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("INSERT INTO todo (item) VALUES (%s)", (todo.item,))
        conn.commit()

        cur.execute("SELECT * FROM todo ORDER BY id")
        todos = cur.fetchall()
        
    return templates.TemplateResponse("todos/todo.html",
    {
        "request": request,
        "todos": todos
    })

@router.get("/", response_model=TodoItems)
def retrieve_todo(request: Request, conn=Depends(get_db_connection)):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM todo ORDER BY id")
        todos = cur.fetchall()

    return templates.TemplateResponse("todos/todo.html", {
        "request": request,
        "todos": todos
    })

@router.get("/{todo_id}")
def get_single_todo(request: Request, todo_id: int = Path(..., title="The ID of the todo to retrieve."), conn=Depends(get_db_connection)):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM todo WHERE id = %s", (todo_id,))
        todo = cur.fetchone()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo with supplied ID doesn't exist",
        )
        
    return templates.TemplateResponse(
        "todos/todo.html", {
        "request": request,
        "todos": [todo] # Pass as a list for consistency with the template
    })

@router.put("/{todo_id}")
def update_todo(todo_data: TodoItem, todo_id: int = Path(..., title="The ID of the todo to be updated."), conn=Depends(get_db_connection)) -> dict:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT id FROM todo WHERE id = %s", (todo_id,))
        todo = cur.fetchone()
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo with supplied ID doesn't exist",
            )
        
        cur.execute("UPDATE todo SET item = %s WHERE id = %s", (todo_data.item, todo_id))
        conn.commit()
        
    return {
        "message": "Todo updated successfully."
    }

@router.delete("/{todo_id}")
def delete_single_todo(todo_id: int, conn=Depends(get_db_connection)) -> dict:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT id FROM todo WHERE id = %s", (todo_id,))
        todo = cur.fetchone()
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo with supplied ID doesn't exist",
            )
        
        cur.execute("DELETE FROM todo WHERE id = %s", (todo_id,))
        conn.commit()

    return {
        "message": "Todo deleted successfully."
    }

@router.delete("/")
def delete_all_todo(conn=Depends(get_db_connection)) -> dict:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE todo RESTART IDENTITY")
        conn.commit()
    return {
        "message": "Todos deleted successfully."
    }