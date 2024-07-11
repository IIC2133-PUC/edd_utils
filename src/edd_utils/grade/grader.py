from pathlib import Path
from dataclasses import dataclass
import csv

from .. import git
from ..tests import get_sorted_tests, StrSortKey
from .types import GetColumnNames
from .storage import GraderStorage


@dataclass
class GraderConfig:
    github_org: str
    get_columns_names: GetColumnNames
    tests_dir: Path = Path("tests")
    repos_dir: Path = Path("repos")


class Grader:
    def __init__(
        self,
        assignment: str,
        dirs_name: str,
        *,
        config: GraderConfig,
        storage_path: Path | None = None,
        test_sorter: StrSortKey | None = None,
    ) -> None:
        self.assignment = assignment
        self.dirs_name = dirs_name
        self.config = config
        self.submissions: list[Submission] = []

        self.tests = get_sorted_tests(self.config.tests_dir / dirs_name, test_sorter)

        storage_path = storage_path or Path(f"{assignment}.tsv")
        columns_names = self.config.get_columns_names([test.key for test in self.tests])
        self.storage = GraderStorage(storage_path, self.tests, columns_names)

    def load_submissions(self, submissions_path: Path):
        reader = csv.reader(submissions_path.open(), delimiter="\t")
        for row in reader:
            if len(row) == 1:
                self.submissions.append(Submission(row[0], None, grader=self))
            elif len(row) >= 2:
                self.submissions.append(Submission(row[0], row[1], grader=self))

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

    def is_saved(self):
        return self.grader.storage.has_user(self.user)

    def save_result(self, key, value):
        self.results[key] = value

    def save(self):
        self.grader.storage.save(self.user, self.results)

    def clone_or_pull(self, branch="origin/main", reset=True):
        """
        Calls git clone or git pull depending on the existence of the repo,
        resets the repo to the latest commit if reset is True,
        and checks out the commit if the submission has a commit.
        """
        if self.repo_path.is_dir():
            if reset:
                git.fetch(self.repo_path)
                git.reset(self.repo_path, branch=branch)

        else:
            self.grader.repos_path.mkdir(parents=True, exist_ok=True)
            git.clone(self.grader.repos_path, self.repo_full_name)

        if self.commit:
            git.checkout(self.repo_path, self.commit)
