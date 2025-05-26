from users.schemas import UserSchema, UserCreate
from auth import utils as auth_utils
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.user import SecurityUser


john = UserSchema(
    username="john",
    password=auth_utils.hash_password("qwerty"),
    email="john@example.com",
)

sam = UserSchema(
    username="sam",
    password=auth_utils.hash_password("secret"),
)

users_db: dict[str, UserSchema] = {
    "john": john,
    "sam": sam,
}


async def registrate_user(session: AsyncSession, user: UserCreate) -> SecurityUser:
    user_dict = user.model_dump()
    user_dict["password"] = auth_utils.hash_password(user_dict.get("password"))
    user = SecurityUser(**user_dict)
    session.add(user)
    await session.commit()
    return user
