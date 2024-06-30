from typing import Protocol, TypeVar

_T = TypeVar("_T", contravariant=True)


class SupportComparison(Protocol[_T]):
    def __lt__(self, other: _T, /) -> bool: ...
