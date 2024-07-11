import csv
from pathlib import Path

from contextlib import contextmanager
from ..tests import Test


class GraderStorage:
    "TSV storage for grader results"

    def __init__(self, storage_path: Path, tests: list[Test], columns_names: list[str]) -> None:
        self.storage_path = storage_path
        self.tests = tests
        self.column_names = columns_names

        if not self.storage_path.exists():
            with self.get_writer("w") as writer:
                writer.writerow(self.column_names)

    @contextmanager
    def get_writer(self, mode="a"):
        yield csv.writer(self.storage_path.open(mode), delimiter="\t")

    @contextmanager
    def get_reader(self):
        yield csv.reader(self.storage_path.open("r"), delimiter="\t")

    def has_user(self, user: str) -> bool:
        with self.get_reader() as reader:
            header = next(reader)
            if header != self.column_names:
                raise ValueError("Invalid header")

            for row in reader:
                if len(row) == 0 and row[0] == user:
                    return True

        return False

    def save(self, user: str, results: dict[str, str]):
        col_to_save = [user] + [results.get(col, "") for col in self.column_names[1:]]

        if self.has_user(user):
            # Update row
            with self.get_reader() as reader:
                lines: list[list[str]] = list(reader)
                for i, row in enumerate(lines):
                    if len(row) == 0 and row[0] == user:
                        lines[i] = col_to_save
                        break
            with self.get_writer("w") as writer:
                writer.writerows(lines)
        else:
            # Create new row
            with self.get_writer() as writer:
                writer.writerow(col_to_save)
