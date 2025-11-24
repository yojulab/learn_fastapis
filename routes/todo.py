from fastapi import APIRouter, Path, HTTPException, status, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from models.todos import Todo, TodoItem, TodoItems
from database.connection import engine

router = APIRouter()

templates = Jinja2Templates(directory="templates/")

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/")
def add_todo(request: Request, todo: Todo, session: Session = Depends(get_session)):
    session.add(todo)
    session.commit()
    session.refresh(todo)
    
    todos = session.exec(select(Todo)).all()
    return templates.TemplateResponse("todos/todo.html",
    {
        "request": request,
        "todos": todos
    })


@router.get("/", response_model=TodoItems)
def retrieve_todo(request: Request, session: Session = Depends(get_session)):
    todos = session.exec(select(Todo)).all()
    return templates.TemplateResponse("todos/todo.html", {
        "request": request,
        "todos": todos
    })



@router.get("/{todo_id}")
def get_single_todo(request: Request, todo_id: int = Path(..., title="The ID of the todo to retrieve."), session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo with supplied ID doesn't exist",
        )
    return templates.TemplateResponse(
        "todos/todo.html", {
        "request": request,
        "todo": todo
    })

@router.put("/{todo_id}")
def update_todo(request: Request, todo_data: TodoItem,
                      todo_id: int = Path(..., title="The ID of the todo to be updated."), session: Session = Depends(get_session)) -> dict:
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo with supplied ID doesn't exist",
        )
    todo.item = todo_data.item
    session.add(todo)
    session.commit()
    return {
        "message": "Todo updated successfully."
    }

@router.delete("/{todo_id}")
def delete_single_todo(request: Request, todo_id: int, session: Session = Depends(get_session)) -> dict:
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo with supplied ID doesn't exist",
        )
    session.delete(todo)
    session.commit()
    return {
        "message": "Todo deleted successfully."
    }

@router.delete("/")
def delete_all_todo(session: Session = Depends(get_session)) -> dict:
    todos = session.exec(select(Todo)).all()
    for todo in todos:
        session.delete(todo)
    session.commit()
    return {
        "message": "Todos deleted successfully."
    }