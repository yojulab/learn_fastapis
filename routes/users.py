import psycopg2
from psycopg2.extras import DictCursor
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from database.connection import get_db_connection
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from models.users import User, TokenResponse
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from utils.paginations import Paginations

router = APIRouter(
    tags=["User"],
)

hash_password = HashPassword()
templates = Jinja2Templates(directory="templates/")

@router.post("/signup")
def sign_user_up(user: User, conn=Depends(get_db_connection)) -> dict:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute('SELECT email FROM "user" WHERE email = %s', (user.email,))
        user_exist = cur.fetchone()

        if user_exist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with email provided exists already."
            )
        
        hashed_password = hash_password.create_hash(user.password)
        
        cur.execute(
            """
            INSERT INTO "user" (name, email, password, manager, sellist1, comment, editorContent)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (user.name, user.email, hashed_password, user.manager, user.sellist1, user.comment, user.editorContent)
        )
        conn.commit()

    return {
        "message": "User created successfully"
    }

@router.post("/signin", response_model=TokenResponse)
def sign_user_in(user: OAuth2PasswordRequestForm = Depends(), conn=Depends(get_db_connection)) -> dict:
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute('SELECT email, password FROM "user" WHERE email = %s', (user.username,))
        user_exist = cur.fetchone()

        if not user_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with email does not exist."
            )
        
        if hash_password.verify_hash(user.password, user_exist['password']):
            access_token = create_access_token(user_exist['email'])
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
    return templates.TemplateResponse(name="users/inserts.html"
                                      , context={'request':request
                                                 , 'first': 5, 'second':6})

@router.post("/login", response_class=HTMLResponse)
async def post_login_form(request:Request):
    form_data = await request.form()
    return templates.TemplateResponse(name="users/login.html"
                                      , context={'request':request
                                                 , 'form_data' : form_data
                                                 , 'first' : 'text'})

@router.get("/login", response_class=HTMLResponse)
def get_login_form(request:Request):
    return templates.TemplateResponse(name="users/login.html", context={'request':request})

@router.get("/insert")
def get_user_insert_form(request:Request):
    return templates.TemplateResponse(name="users/login.html", context={'request':request})

@router.post("/insert")
async def post_user_insert_form(request:Request, conn=Depends(get_db_connection)):
    user_dict = dict(await request.form())
    
    with conn.cursor(cursor_factory=DictCursor) as cur:
        # 저장
        cur.execute(
            """
            INSERT INTO "user" (name, email, password, manager, sellist1, comment, editorContent)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (user_dict.get('name'), user_dict.get('email'), 
             hash_password.create_hash(user_dict.get('password', '')), 
             user_dict.get('manager'), user_dict.get('sellist1'), 
             user_dict.get('comment'), user_dict.get('editorContent'))
        )
        conn.commit()

        # 리스트 정보
        cur.execute('SELECT * FROM "user" ORDER BY id')
        user_list = cur.fetchall()
    
    return templates.TemplateResponse(name="users/list_jinja.html"
                                      , context={'request':request
                                                 , 'users' : user_list })

@router.get("/list")
def get_user_list(request:Request):
    return templates.TemplateResponse(name="users/list.html"
                                      , context={'request':request})

@router.get("/list_jinja")
def get_user_list_jinja(request:Request, conn=Depends(get_db_connection)):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute('SELECT * FROM "user" ORDER BY id')
        user_list = cur.fetchall()

    return templates.TemplateResponse(name="users/list_jinja.html"
                                      , context={'request':request
                                                 , 'users' : user_list })

@router.get("/list_jinja_pagination/{page_number}")
@router.get("/list_jinja_pagination")
def get_user_list_jinja_pagination(request:Request, page_number: Optional[int] = 1, conn=Depends(get_db_connection)):
    user_dict = dict(request.query_params)
    search_word = user_dict.get("word")
    key_name = user_dict.get("key_name")
    
    #
    #
    allowed_columns = ["name", "email", "manager"] 
    
    with conn.cursor(cursor_factory=DictCursor) as cur:
        base_query = ' FROM "user"'
        where_clause = ""
        params = []

        if search_word and key_name in allowed_columns:
            where_clause = f" WHERE {key_name} ILIKE %s"
            params.append(f"%{search_word}%")

        # Get total records
        cur.execute(f"SELECT COUNT(*) {base_query}{where_clause}", tuple(params))
        total_records = cur.fetchone()[0]
        
        pagination = Paginations(total_records=total_records, current_page=page_number)
        
        # Get records for the current page
        query = f"SELECT * {base_query}{where_clause} ORDER BY id LIMIT %s OFFSET %s"
        params.extend([pagination.records_per_page, pagination.start_record_number])
        cur.execute(query, tuple(params))
        user_list = cur.fetchall()
    
    return templates.TemplateResponse(name="/users/list_jinja_paginations.html"
                                      , context={'request':request
                                                 , 'users' : user_list
                                                 , 'pagination' : pagination })

@router.get("/search")
def search_users(request:Request, conn=Depends(get_db_connection)):
    user_dict = dict(request.query_params)
    search_word = user_dict.get("word")
    key_name = user_dict.get("key")
    
    allowed_columns = ["name", "email", "manager"]

    with conn.cursor(cursor_factory=DictCursor) as cur:
        if search_word and key_name in allowed_columns:
            cur.execute(f'SELECT * FROM "user" WHERE {key_name} ILIKE %s ORDER BY id', (f"%{search_word}%",))
        else:
            cur.execute('SELECT * FROM "user" ORDER BY id')
        
        user_list = cur.fetchall()

    return templates.TemplateResponse(name="users/list_jinja.html"
                                      , context={'request':request
                                                 , 'users' : user_list })

@router.get("/read/{object_id}")
def read_user(request:Request, object_id:int, conn=Depends(get_db_connection)):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute('SELECT * FROM "user" WHERE id = %s', (object_id,))
        user = cur.fetchone()
    
    return templates.TemplateResponse(name="users/reads.html"
                                      , context={'request':request
                                                 , 'user':user})

