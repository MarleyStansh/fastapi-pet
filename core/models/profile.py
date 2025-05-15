from typing import TYPE_CHECKING
from .base import Base
from .mixins import UserRelationshipMixin
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Profile(Base, UserRelationshipMixin):
    _user_id_unique = True
    _user_back_populates = "profile"

    first_name: Mapped[str | None] = mapped_column(String(40))
    last_name: Mapped[str | None] = mapped_column(String(40))
    bio: Mapped[str | None]
