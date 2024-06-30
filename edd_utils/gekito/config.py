from logging import Logger, getLogger
from pathlib import Path
from typing import TypeVar, Union, Sequence, Iterable
from os import PathLike

ProgressType = TypeVar("ProgressType")


def noop_track(
    sequence: Union[Sequence[ProgressType], Iterable[ProgressType]], description: str
) -> Iterable[ProgressType]:
    return sequence


logger = getLogger(__name__)
logger.setLevel("ERROR")


class Config:
    def __init__(self, *, output_dir: str | PathLike[str] = Path("tests"), logger: Logger = logger, track=noop_track):
        self.output_dir = Path(output_dir)
        self.logger = logger
        self.track = track
