from typing import Optional
from sqlmodel import SQLModel
from pydantic import BaseModel, EmailStr


class User(SQLModel):
    id: Optional[int] = None
    name: Optional[str] = None
    email: EmailStr
    password: str
    manager: Optional[str] = None
    sellist1 : Optional[str] = None
    comment : Optional[str] = None
    editorContent : Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str