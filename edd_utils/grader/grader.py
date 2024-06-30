from pathlib import Path
from typing import Callable, TypeAlias
from dataclasses import dataclass
import csv

from . import git
from .types import SupportComparison
from .test import Test
from .storage import GraderStorage

StrSortKey: TypeAlias = Callable[[str, str], SupportComparison]


@dataclass
class GraderConfig:
    github_org: str
    get_columns_names: Callable[[list[str]], list[str]]
    timeout: int = 10
    mbs_limit: int = 1024
    tests_dir: Path = Path("tests")
    repos_dir: Path = Path("repos")


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


class Grader:
    def __init__(
        self,
        # tha name of the assignment
        assignment: str,
        dirs_name: str,
        # a tsv file that contains the usernames and (optional) commit to grade
        # it should not contain a header
        submissions_path: Path,
        *,
        # shared configuration for the grader
        config: GraderConfig,
        # a tsv file where the results will be stored
        storage_path: Path | None = None,
        # the order of the test cases
        test_sorter: StrSortKey | None = None,
    ) -> None:
        self.assignment = assignment
        self.dirs_name = dirs_name
        self.config = config
        self.tests = get_tests(self.config.tests_dir / dirs_name, test_sorter)

        storage_path = storage_path or Path(f"{assignment}.tsv")
        self.storage = GraderStorage(storage_path, self.tests, self.config.get_columns_names)
        self.submissions = self.__get_submissions(submissions_path)

    def __get_submissions(self, submissions_path: Path):
        reader = csv.reader(submissions_path.open(), delimiter="\t")
        submissions: list[Submission] = []
        for row in reader:
            if len(row) == 1:
                submission = Submission(row[0], None, grader=self)
            else:
                submission = Submission(row[0], row[1], grader=self)
            submissions.append(submission)
        return submissions

    @property
    def repos_path(self):
        return self.config.repos_dir / self.dirs_name


class Submission:
    def __init__(self, user: str, commit: str | None, *, grader: Grader):
        self.user = user
        self.commit = commit
        self.grader = grader
        self.results: dict[str, str] = {}

    @property
    def repo_name(self):
        # Use GitHub Education Classroom naming convention
        return f"{self.grader.assignment}-{self.user}"

    @property
    def repo_path(self):
        return self.grader.repos_path / self.repo_name

    @property
    def repo_full_name(self):
        return f"{self.grader.config.github_org}/{self.repo_name}"

    def has_run(self):
        return self.grader.storage.has_user(self.user)

    def save_result(self, key, value):
        self.results[key] = value

    def save(self):
        self.grader.storage.save(self.user, self.results)

    def clone_or_pull(self, branch="origin/main", reset=True):
        if self.repo_path.is_dir():
            if reset:
                git.fetch(self.repo_path)
                git.reset(self.repo_path, branch=branch)

        else:
            self.grader.repos_path.mkdir(parents=True, exist_ok=True)
            git.clone(self.grader.repos_path, self.repo_full_name)

        if self.commit:
            git.checkout(self.repo_path, self.commit)
