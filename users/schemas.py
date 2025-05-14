from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr


class CreateUser(BaseModel):
    username: Annotated[str, MinLen(8), MaxLen(30)]
    email: EmailStr
