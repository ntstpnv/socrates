from typing import TYPE_CHECKING

from sqlalchemy import SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.models.base import Base


if TYPE_CHECKING:
    from bot.db.models.students import Student


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(
        SmallInteger,
        init=False,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        Text,
        unique=True,
    )

    students: Mapped[list["Student"]] = relationship(
        back_populates="group",
        default_factory=list,
    )
