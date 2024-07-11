import os
from typing import TypeAlias, Sequence


StrOrBytesPath: TypeAlias = str | bytes | os.PathLike[str] | os.PathLike[bytes]
CMD: TypeAlias = Sequence[StrOrBytesPath]
