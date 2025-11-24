from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from database.connection import engine
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from models.users import User, TokenResponse
from sqlmodel import Session, select
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from utils.paginations import Paginations

router = APIRouter(
    tags=["User"],
)

hash_password = HashPassword()
templates = Jinja2Templates(directory="templates/")

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/signup")
def sign_user_up(user: User, session: Session = Depends(get_session)) -> dict:
    user_exist = session.exec(select(User).where(User.email == user.email)).first()

    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email provided exists already."
        )
    hashed_password = hash_password.create_hash(user.password)
    user.password = hashed_password
    session.add(user)
    session.commit()
    session.refresh(user)
    return {
        "message": "User created successfully"
    }

@router.post("/signin", response_model=TokenResponse)
def sign_user_in(user: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)) -> dict:
    user_exist = session.exec(select(User).where(User.email == user.username)).first()
    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with email does not exist."
        )
    if hash_password.verify_hash(user.password, user_exist.password):
        access_token = create_access_token(user_exist.email)
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed."
    )

@router.get("/form")
def get_insert_form(request:Request):
    print(dict(request._query_params))
    return templates.TemplateResponse(name="users/inserts.html"
                                      , context={'request':request
                                                 , 'first': 5, 'second':6})

@router.post("/login", response_class=HTMLResponse)
def post_login_form(request:Request):
    form_data = dict(request.form())
    print(form_data)
    return templates.TemplateResponse(name="users/login.html"
                                      , context={'request':request
                                                 , 'form_data' : form_data
                                                 , 'first' : 'text'})

@router.get("/login", response_class=HTMLResponse)
def get_login_form(request:Request):
    print(dict(request._query_params))
    return templates.TemplateResponse(name="users/login.html", context={'request':request})

@router.get("/insert")
def get_user_insert_form(request:Request):
    print(dict(request._query_params))
    return templates.TemplateResponse(name="users/login.html", context={'request':request})

@router.post("/insert")
def post_user_insert_form(request:Request, session: Session = Depends(get_session)):
    user_dict = dict(request.form())
    print(user_dict)
    # 저장
    user = User(**user_dict)
    session.add(user)
    session.commit()
    session.refresh(user)

    # 리스트 정보
    user_list = session.exec(select(User)).all()
    return templates.TemplateResponse(name="users/list_jinja.html"
                                      , context={'request':request
                                                 , 'users' : user_list })

@router.get("/list")
def get_user_list(request:Request):
    return templates.TemplateResponse(name="users/list.html"
                                      , context={'request':request})

@router.get("/list_jinja")
def get_user_list_jinja(request:Request, session: Session = Depends(get_session)):
    print(dict(request._query_params))
    
    user_list = session.exec(select(User)).all()

    return templates.TemplateResponse(name="users/list_jinja.html"
                                      , context={'request':request
                                                 , 'users' : user_list })

@router.get("/list_jinja_pagination/{page_number}")
@router.get("/list_jinja_pagination")
def get_user_list_jinja_pagination(request:Request, page_number: Optional[int] = 1, session: Session = Depends(get_session)):
    user_dict = dict(request._query_params)
    print(user_dict)
    
    conditions = []
    try :
        search_word = user_dict["word"]
    except:
        search_word = None
    if search_word:
        conditions.append(getattr(User, user_dict['key_name']).like(f"%{search_word}%"))
    
    query = select(User).where(*conditions)
    
    total_records = len(session.exec(query).all())
    pagination = Paginations(total_records=total_records, current_page=page_number)
    
    user_list = session.exec(query.offset(pagination.start_record_number).limit(pagination.records_per_page)).all()
    
    return templates.TemplateResponse(name="/users/list_jinja_paginations.html"
                                      , context={'request':request
                                                 , 'users' : user_list
                                                  ,'pagination' : pagination })

@router.get("/search")
def search_users(request:Request, session: Session = Depends(get_session)):
    user_dict = dict(request._query_params)
    print(user_dict)
    
    conditions = []
    try:
        search_word = user_dict["word"]
    except:
        search_word = None
    if search_word:
        conditions.append(getattr(User, user_dict['key']).like(f"%{search_word}%"))

    user_list = session.exec(select(User).where(*conditions)).all()
    return templates.TemplateResponse(name="users/list_jinja.html"
                                      , context={'request':request
                                                 , 'users' : user_list })

@router.get("/read/{object_id}")
def read_user(request:Request, object_id:int, session: Session = Depends(get_session)):
    print(dict(request._query_params))
    user = session.get(User, object_id)
    return templates.TemplateResponse(name="users/reads.html"
                                      , context={'request':request
                                                 , 'user':user})
