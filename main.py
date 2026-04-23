from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import task, user, category
from database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: Creating database tables...")
    await init_db()
    yield 

    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

app.include_router(task.router)
app.include_router(user.router)
app.include_router(category.router)