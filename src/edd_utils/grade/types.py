from typing import Protocol, TypeVar, TypeAlias, Callable

_T = TypeVar("_T", contravariant=True)


class SupportComparison(Protocol[_T]):
    def __lt__(self, other: _T, /) -> bool: ...


GetColumnNames: TypeAlias = Callable[[list[str]], list[str]]
