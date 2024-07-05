from abc import ABCMeta, abstractmethod

from pathlib import Path
from shutil import rmtree
from typing import Generator, Generic, TypeVar, final

from .config import Config

_TestCaseVars = TypeVar("_TestCaseVars")


class TestGroupMeta(ABCMeta):
    slug: str
    config: Config = Config()

    @property
    def group_dir(cls) -> Path:
        return cls.config.output_dir / cls.slug


class TestGroup(Generic[_TestCaseVars], metaclass=TestGroupMeta):
    """
    Base class for test case generation.

    ```python
    class ExampleVariables():
        def __init__(self, a: int = 1):
            self.a = a

    class ExampleTestGroup(TestGroup[ExampleVariables]):
        config = Config()  # optional

        @classmethod
        def collect_tests(cls):
            yield "a", ExampleVariables(a=5)
            yield "b", ExampleVariables(a=2)

        def build_test(self):
            input = self.get_path("input.txt")

            with input.open("w") as f:
                f.write(str(self.vars.a))

            return {"run": ["./program", input, self.get_path("expected.txt")]}

    meta = {ExampleTestGroup.slug: ExampleTestGroup.generate()}
    print(meta)
    ```
    """

    # Internal

    @classmethod
    def __iter_valid_test_cases(cls):
        prev_test_cases = set()

        for test_slug, test_vars in cls.collect_tests():
            if test_slug in prev_test_cases:
                cls.config.logger.error("Duplicate test case slug %s, skipping", test_slug)
                continue

            prev_test_cases.add(test_slug)
            yield test_slug, test_vars

    # External

    @final
    @classmethod
    def generate(cls):
        "Runs the test case generation for the group."

        rmtree(cls.group_dir, ignore_errors=True)
        cls.group_dir.mkdir(parents=True)

        cls.config.logger.info("Collecting test cases for %s", cls.slug)
        pre_collected_test_cases = list(cls.__iter_valid_test_cases())

        cls.config.logger.info("Generating test cases for %s", cls.slug)
        desc = f"Generating {cls.slug}"
        group_meta = {}
        for test_slug, test_vars in cls.config.track(pre_collected_test_cases, desc):
            test_dir = cls.group_dir / test_slug
            test_dir.mkdir()

            meta = cls(vars=test_vars, test_dir=test_dir).build_test()

            if meta is not None:
                group_meta[test_slug] = meta

        return group_meta

    # Instance initialization test case

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "slug"):
            cls.slug = cls.__name__.lower()

    @final
    def __init__(self, vars: _TestCaseVars, test_dir: Path):
        """You should't initialize this class directly."""

        self.vars = vars
        self.__test_dir = test_dir

    # Method that should be implemented

    @abstractmethod
    def build_test(self):
        """
        Method called on each test case generation.
        Use self.var to access the test case variables.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def collect_tests(cls) -> Generator[tuple[str, _TestCaseVars], None, None]:
        """Called to collect all test cases, in the format (slug, vars)"""
        raise NotImplementedError

    # Provided methods and properties

    def open(self, file: str, mode: str = "w"):
        """Opens a file in the test directory. Defaults to write mode."""
        return (self.__test_dir / file).open(mode)

    def get_path(self, file: str) -> Path:
        """Gets a path for a file in the test directory."""
        return self.__test_dir / file

    @property
    def dir(self) -> Path:
        """The directory for the current test case."""
        return self.__test_dir
