from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, SmallInteger, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.models.base import Base


if TYPE_CHECKING:
    from bot.db.models.groups import Group


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (UniqueConstraint("name", "group_id"),)

    id: Mapped[int] = mapped_column(
        SmallInteger,
        init=False,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(Text)

    group_id: Mapped[int] = mapped_column(
        ForeignKey(
            "groups.id",
            ondelete="CASCADE",
        ),
        init=False,
        index=True,
    )

    group: Mapped["Group"] = relationship(
        back_populates="students",
        default=None,
    )
