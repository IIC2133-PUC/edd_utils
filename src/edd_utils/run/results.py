from dataclasses import dataclass
from enum import Enum


class ErrorStatus(Enum):
    MEMORY_EXCEEDED = "MEMORY EXCEEDED"
    SEGFAULT = "SEGFAULT"
    TIMEOUT = "TIMEOUT"
    BUSEXIT = "BUSEXIT"
    RUNTIME_ERROR = "RUNTIME ERROR"
    INCORRECT_OUTPUT = "INCORRECT OUTPUT"


@dataclass(frozen=True, slots=True)
class ResultError:
    status: ErrorStatus


@dataclass(frozen=True, slots=True)
class ResultOk:
    pass
