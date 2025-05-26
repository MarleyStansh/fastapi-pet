from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
)
from users.schemas import UserSchema
from pydantic import BaseModel
from auth import utils as auth_utils
from api_v1.demo_auth.helpers import (
    create_access_token,
    create_refresh_token,
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
)
from api_v1.demo_auth.validation import (
    get_current_auth_user,
    get_current_auth_user_for_refresh,
    get_current_token_payload,
)
from .crud import users_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result
from core.models.user import SecurityUser
from core.models import db_helper


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


http_bearer = HTTPBearer(auto_error=False)


router = APIRouter(prefix="/jwt", tags=["JWT"], dependencies=[Depends(http_bearer)])


async def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )
    stmt = select(SecurityUser).where(SecurityUser.username == username)
    result: Result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise unauthed_exc
    if not auth_utils.validate_password(
        password=password, hashed_password=user.password
    ):
        raise unauthed_exc
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    return user


def get_current_active_auth_user(
    user: UserSchema = Depends(get_current_auth_user),
):
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User is not active",
    )


@router.post("/login/", response_model=TokenInfo)
async def auth_user_issue_jwt(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    user: UserSchema = Depends(validate_auth_user),
):
    access_token = create_access_token(user=user)
    refresh_token = create_refresh_token(user=user)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh/", response_model=TokenInfo, response_model_exclude_none=True)
def auth_refresh_jwt(
    user: UserSchema = Depends(get_current_auth_user_for_refresh),
):
    access_token = create_access_token(user)
    return TokenInfo(access_token=access_token)


@router.get("/users/me/")
def auth_user_self_check_info(
    user: UserSchema = Depends(get_current_active_auth_user),
    payload: dict = Depends(get_current_token_payload),
):
    iat = payload.get("iat")
    return {
        "username": user.username,
        "email": user.email,
        "logged_in_at": iat,
    }
