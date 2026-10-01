from asyncio import Lock
from collections import deque
from collections.abc import Callable
from typing import Any, Protocol

from aiolimiter import AsyncLimiter
from maxapi.context import MemoryContext

from bot.settings import ADMINS


class AnyContext(Protocol):
    @property
    def context(self) -> dict[str, Any]: ...


class Field:
    __slots__ = ("name", "default", "factory")

    def __init__(self, default: Any = None, factory: Callable[[], Any] | None = None) -> None:
        self.default = default
        self.factory = factory

    def __set_name__(self, _, name: str) -> None:
        self.name = name

    def __get__(self, obj: AnyContext | None, *args) -> Any:
        if obj is None:
            return self
        elif self.name not in obj.context:
            obj.context[self.name] = self.default if self.factory is None else self.factory()
        return obj.context[self.name]

    def __set__(self, obj: AnyContext, value: Any) -> None:
        obj.context[self.name] = value


class Context(MemoryContext):
    full_name = Field()

    branch = Field()
    step = Field(default=0)

    message_id = Field()

    group_id = Field()
    group = Field()

    student_id = Field()
    student = Field()

    test_id = Field()
    test = Field()

    texts = Field(factory=deque)
    options = Field(factory=deque)
    answers = Field(factory=list)

    def __init__(self, chat_id: int | None, user_id: int | None, **kwargs) -> None:
        super().__init__(chat_id, user_id, **kwargs)
        self.lock = Lock()
        self.limiter = AsyncLimiter(2, 1)
        self.is_admin = user_id in ADMINS

    @property
    def context(self) -> dict[str, Any]:
        return self._context

    @property
    def user(self) -> str:
        return f"{self.user_id} {self.full_name}"

    @property
    def state(self) -> str | None:
        return f"{self.branch.__name__}{self.step}" if self.step else None

    def next_state(self) -> None:
        self.step += 1
        self._state = self.branch.get_state(self.step)

    def rollback(self) -> None:
        self.step -= 1
        self._state = self.branch.get_state(self.step)
