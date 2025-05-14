from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel, EmailStr

from core.models import Base, db_helper

from items_views import router as items_router
from users.views import router as users_router

import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(items_router)
app.include_router(users_router)


@app.get("/")
def root():
    return "Hello World"


@app.get("/hello/")
def hello(name: str = "world"):
    name = name.title().strip()
    return {"message": f"Hello, {name}"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
