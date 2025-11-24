from typing import Optional, List
from sqlmodel import Field, SQLModel, JSON, Column
from pydantic import BaseModel


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    creator: Optional[str]
    title: str
    image: str
    description: str
    tags: List[str] = Field(sa_column=Column(JSON))
    location: str


class EventUpdate(BaseModel):
    title: Optional[str]
    image: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]
    location: Optional[str]