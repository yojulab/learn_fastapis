from typing import Optional, List
from sqlmodel import SQLModel
from pydantic import BaseModel


class Event(SQLModel):
    id: Optional[int] = None
    creator: Optional[str] = None
    title: str
    image: str
    description: str
    tags: List[str]
    location: str


class EventUpdate(BaseModel):
    title: Optional[str]
    image: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]
    location: Optional[str]