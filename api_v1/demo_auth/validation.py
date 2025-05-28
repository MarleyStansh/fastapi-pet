from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from .schemas import UserSchema
from sqlalchemy.ext.asyncio import AsyncSession
from auth import utils as auth_utils
from api_v1.demo_auth.helpers import (
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
)
from core.models import db_helper
from sqlalchemy import select, Result
from core.models.user import SecurityUser


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/demo_auth/jwt/login/",
)


async def validate_token_type(
    payload: dict,
    token_type: str,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid token type: {current_token_type}, when {token_type!r} is expected.",
    )


async def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> UserSchema:
    try:
        payload = auth_utils.decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid token error: {e}"
        )
    return payload


async def get_user_by_token_sub(
    payload: dict,
    session: AsyncSession,
) -> UserSchema:
    print(session)
    username: str | None = payload.get("sub")
    user = await find_scalar_user_by_username(username=username, session=session)
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token is invalid (user is not found)",
    )


async def get_current_auth_user(
    token_type: str = ACCESS_TOKEN_TYPE,
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> UserSchema:
    await validate_token_type(payload=payload, token_type=token_type)
    user = await get_user_by_token_sub(payload=payload, session=session)
    return user


async def get_current_auth_user_for_refresh(
    token_type: str = REFRESH_TOKEN_TYPE,
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> UserSchema:
    await validate_token_type(payload=payload, token_type=token_type)
    user = await get_user_by_token_sub(payload=payload, session=session)
    return user


async def find_scalar_user_by_username(
    username: str,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> UserSchema:
    stmt = select(SecurityUser).where(SecurityUser.username == username)
    result: Result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user
