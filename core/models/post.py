from typing import TYPE_CHECKING


from .base import Base
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .mixins import UserRelationshipMixin


class Post(Base, UserRelationshipMixin):
    _user_back_populates = "posts"

    title: Mapped[str] = mapped_column(String(100), unique=True)
    body: Mapped[str] = mapped_column(
        Text,
        default="",
        server_default="",
    )

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, username{self.title!r}, user_id={self.user_id})"

    def __repr__(self):
        return str(self)
