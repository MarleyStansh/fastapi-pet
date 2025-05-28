from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
)
from .schemas import UserSchema
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
    find_scalar_user_by_username,
)
from .crud import register_user
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import db_helper
from .schemas import UserCreate


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


http_bearer = HTTPBearer(auto_error=False)


router = APIRouter(
    prefix="/jwt", tags=["JWT-Auth"], dependencies=[Depends(http_bearer)]
)


async def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )
    user = await find_scalar_user_by_username(username=username, session=session)
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


async def get_current_active_auth_user(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
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
    access_token = await create_access_token(user=user, session=session)
    refresh_token = await create_refresh_token(user=user, session=session)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh/", response_model=TokenInfo, response_model_exclude_none=True)
async def auth_refresh_jwt(
    user: UserSchema = Depends(get_current_auth_user_for_refresh),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    access_token = await create_access_token(user=user, session=session)
    return TokenInfo(access_token=access_token)


@router.get("/users/me/")
async def auth_user_self_check_info(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    user: UserSchema = Depends(get_current_active_auth_user),
    payload: dict = Depends(get_current_token_payload),
):
    iat = payload.get("iat")
    return {
        "username": user.username,
        "email": user.email,
        "logged_in_at": iat,
    }


@router.post(
    "/register/", response_model=UserCreate, status_code=status.HTTP_201_CREATED
)
async def register_user_with_form(
    user_in: UserCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await register_user(
        session=session,
        user=user_in,
    )
