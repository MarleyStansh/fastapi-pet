from typing import Annotated

from fastapi import FastAPI, Path
from pydantic import BaseModel, EmailStr

import uvicorn

app = FastAPI()


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

@app.get("/items/latest/")
def get_latest_item():
    return {"item_id": 0, "name": "latest"}

@app.get("/items/")
def list_items():
    return [
        "item1",
        "item2",
        "item3"
    ]

@app.get("/items/{item_id}/")
def get_item_by_id(item_id: Annotated[int, Path(ge=1, lt=1_000_000)]):
    return {
        "item_id": item_id,
        "name": "no_name"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)