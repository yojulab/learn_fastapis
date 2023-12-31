import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from database.connection import Settings
from routes.events import event_router
from routes.users import user_router
from routes.todo import todo_router


app = FastAPI()

settings = Settings()

# 라우트 등록

app.include_router(user_router, prefix="/user")
app.include_router(event_router, prefix="/event")
app.include_router(todo_router, prefix='/todo')


@app.on_event("startup")
async def init_db():
    await settings.initialize_database()


@app.get("/")
async def home():
    return RedirectResponse(url="/todo/")


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
