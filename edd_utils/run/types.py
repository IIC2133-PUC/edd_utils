import os
import typing

StrOrBytesPath: typing.TypeAlias = str | bytes | os.PathLike[str] | os.PathLike[bytes]
CMD: typing.TypeAlias = typing.Sequence[StrOrBytesPath]
