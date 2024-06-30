import os
import resource
import signal

from .results import ResultError, ResultOk, ErrorStatus
from .popen import PopenWithWait4
from .types import CMD, StrOrBytesPath


class ResourceLimiter:
    def __init__(self, timeout: int | None, mbs_limit: int | None):
        self.timeout = timeout
        self.mbs_limit = mbs_limit

    def __call__(self):
        self._limit_cpu()
        self._limit_memory()

    def _limit_cpu(self):
        if self.timeout is None:
            return
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (self.timeout, resource.RLIM_INFINITY))
        except ValueError:
            pass

    def _limit_memory(self):
        if self.mbs_limit is None:
            return
        try:
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            resource.setrlimit(resource.RLIMIT_AS, (self.mbs_limit * 1024 * 1024, hard))
        except ValueError:
            pass


def run_command(
    args: CMD, *, cwd: StrOrBytesPath | None = None, timeout: int | None = None, mbs_limit: int | None = 1024
) -> ResultError | ResultOk:
    resource_limiter = ResourceLimiter(timeout, mbs_limit)
    process = PopenWithWait4(args, cwd=cwd, preexec_fn=resource_limiter)
    status, resource_usage = process.wait4(timeout=timeout)

    used_memory_on_mb = resource_usage.ru_maxrss / (resource.getpagesize() * 1024)

    if mbs_limit is not None and used_memory_on_mb > mbs_limit:
        return ResultError(ErrorStatus.MEMORY_EXCEEDED)

    elif os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0:
        return ResultOk()

    elif os.WIFSIGNALED(status):
        process_signal = os.WTERMSIG(status)
        if process_signal == signal.SIGSEGV:
            return ResultError(ErrorStatus.SEGFAULT)
        elif process_signal == signal.SIGBUS:
            return ResultError(ErrorStatus.BUSEXIT)
        elif process_signal == signal.SIGKILL:
            return ResultError(ErrorStatus.TIMEOUT)
        elif process_signal == signal.SIGXCPU:
            return ResultError(ErrorStatus.TIMEOUT)

    return ResultError(ErrorStatus.RUNTIME_ERROR)
