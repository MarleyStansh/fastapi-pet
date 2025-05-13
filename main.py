from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

from items_views import router as items_router

import uvicorn

app = FastAPI()
app.include_router(items_router)


class CreateUser(BaseModel):
    email: EmailStr

@app.get("/")
def root():
    return "Hello World"

@app.get("/hello/")
def hello(name: str = "world"):
    name = name.title().strip()
    return {"message": f"Hello, {name}"}

@app.post("/users/")
def create_user(user: CreateUser):
    return {
        "message": "success",
        "user": user.email
    }


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)