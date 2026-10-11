from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from bot.db.models.base import Base


class Result(Base):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(
        init=False,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(BigInteger)
    full_name: Mapped[str] = mapped_column(Text)

    group_id: Mapped[int] = mapped_column(
        ForeignKey(
            "groups.id",
            ondelete="CASCADE",
        ),
        index=True,
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey(
            "students.id",
            ondelete="CASCADE",
        ),
        index=True,
    )
    test_id: Mapped[int] = mapped_column(
        ForeignKey(
            "tests.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    finished_at: Mapped[datetime]
    answers: Mapped[str] = mapped_column(Text)
    points: Mapped[int] = mapped_column(SmallInteger)
