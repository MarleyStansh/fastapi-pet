from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel, EmailStr

from core.config import settings

from api_v1 import router as router_v1

from items_views import router as items_router
from users.views import router as users_router

import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=router_v1, prefix=settings.api_v1_prefix)
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
