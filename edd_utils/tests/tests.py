from typing import Callable, TypeAlias

from pathlib import Path


from typing import Protocol, TypeVar

_T = TypeVar("_T", contravariant=True)


class SupportComparison(Protocol[_T]):
    def __lt__(self, other: _T, /) -> bool: ...


StrSortKey: TypeAlias = Callable[[str, str], SupportComparison]


def get_tests(test_dir: Path, test_sorter: StrSortKey | None = None):
    tests: list[Test] = []
    for group in test_dir.iterdir():
        if not group.is_dir():
            continue

        for test in group.iterdir():
            if not test.is_dir():
                continue

            tests.append(Test(test))

    if test_sorter is not None:
        tests.sort(key=lambda test: test_sorter(test.group, test.name))

    return tests


class Test:
    def __init__(self, test_path: Path) -> None:
        self.path = test_path
        self.name = test_path.name
        self.group = test_path.parent.name
        self.key = f"{self.group}/{self.name}"

    def __str__(self) -> str:
        return self.key
