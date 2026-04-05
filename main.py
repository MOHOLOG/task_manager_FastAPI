from fastapi import FastAPI
from routers import task, user, category
from database import init_db

init_db()

app = FastAPI()
app.include_router(task.router)
app.include_router(user.router)
app.include_router(category.router)