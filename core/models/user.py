from typing import TYPE_CHECKING
from .base import Base

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .post import Post
    from .profile import Profile


class User(Base):

    username: Mapped[str] = mapped_column(String(32), unique=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="user")

    profile: Mapped["Profile"] = relationship(back_populates="user")

    password: Mapped[str]

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, username{self.username!r})"

    def __repr__(self):
        return str(self)


class SecurityUser(Base):

    username: Mapped[str] = mapped_column(String(32), unique=True)

    password: Mapped[str]

    email: Mapped[str | None]

    active: Mapped[bool] = mapped_column(default=True)
