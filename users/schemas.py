from typing import Annotated, ClassVar
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, ConfigDict, EmailStr


class CreateUser(BaseModel):
    username: Annotated[str, MinLen(8), MaxLen(30)]
    email: EmailStr


class UserSchema(BaseModel):
    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True

    model_config: ClassVar = ConfigDict(strict=True)
