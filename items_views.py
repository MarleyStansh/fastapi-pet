from typing import Annotated

from fastapi import APIRouter, Path


router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/latest/")
def get_latest_item():
    return {"item_id": 0, "name": "latest"}

@router.get("/")
def list_items():
    return [
        "item1",
        "item2",
        "item3"
    ]

@router.get("/{item_id}/")
def get_item_by_id(item_id: Annotated[int, Path(ge=1, lt=1_000_000)]):
    return {
        "item_id": item_id,
        "name": "no_name"
    }