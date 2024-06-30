from pathlib import Path


class Test:
    def __init__(self, test_path: Path) -> None:
        self.path = test_path
        self.name = test_path.name
        self.group = test_path.parent.name
        self.key = f"{self.group}/{self.name}"

    def __str__(self) -> str:
        return self.key
