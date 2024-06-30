from typing import Generic, TypeVar
import random

T = TypeVar("T")


class Assigner(Generic[T]):
    def __init__(self, pool: list[T]):
        self._pool = pool
        self._count = {k: 0 for k in pool}

    def get_random(self) -> T:
        min_count = min(self._count.values())
        selected = random.choice([option for option in self._pool if self._count[option] == min_count])
        self._count[selected] += 1
        return selected

    def reset(self):
        self._count = {k: 0 for k in self._pool}
