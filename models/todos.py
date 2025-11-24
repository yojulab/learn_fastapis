from typing import List, Optional

from fastapi import Form
from pydantic import BaseModel
from sqlmodel import SQLModel


class Todo(SQLModel):
    id: Optional[int] = None
    item: str

    @classmethod
    def as_form(
        self,
        item: str = Form(...)
    ):
        return self(item=item)


class TodoItem(BaseModel):
    item: str

    class Config:
        json_schema_extra = {
            "example": {
                "item": "Read the next chapter of the book"
            }
        }


class TodoItems(BaseModel):
    todos: List[TodoItem]

    class Config:
        json_schema_extra = {
            "example": {
                "todos": [
                    {
                        "item": "Example schema 1!"
                    },
                    {
                        "item": "Example schema 2!"
                    }
                ]
            }
        }