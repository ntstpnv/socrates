from functools import lru_cache

from maxapi.context import State, StatesGroup


class Admin(StatesGroup):
    State1 = State()
    State2 = State()
    State3 = State()

    @classmethod
    @lru_cache(maxsize=1)
    def _states(cls) -> dict[int, State | None]:
        return {
            0: None,
            1: cls.State1,
            2: cls.State2,
            3: cls.State3,
        }

    @classmethod
    def get_state(cls, step: int) -> State | None:
        return cls._states().get(step)


class User(StatesGroup):
    State1 = State()
    State2 = State()
    State3 = State()
    State4 = State()
    State5 = State()

    @classmethod
    @lru_cache(maxsize=1)
    def _states(cls) -> dict[int, State | None]:
        return {
            0: None,
            1: cls.State1,
            2: cls.State2,
            3: cls.State3,
            4: cls.State4,
            5: cls.State5,
        }

    @classmethod
    def get_state(cls, step: int) -> State | None:
        return cls._states().get(step, User.State5)
