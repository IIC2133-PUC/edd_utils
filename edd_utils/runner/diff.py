import os
import subprocess
from pathlib import Path

from .run import ErrorStatus, ResultError, ResultOk, run_command


class InputOutputRunner:
    def __init__(self, timeout: int = 10, mbs_limit: int = 1024):
        self.timeout = timeout
        self.mbs_limit = mbs_limit

    def run(self, program_name: str, input_file: Path, output_file: Path, expected_output: Path, *, cwd: os.PathLike):
        args = [f"./{program_name}", str(input_file), str(output_file)]
        result = run_command(args, cwd=cwd, timeout=self.timeout, mbs_limit=self.mbs_limit)

        if isinstance(result, ResultError):
            return result

        diff_options = ["--ignore-space-change", "--ignore-blank-lines", "--brief"]
        diff_args = ["diff", *diff_options, str(output_file), str(expected_output)]
        diff_result = subprocess.run(diff_args, cwd=cwd, stdout=subprocess.DEVNULL)

        if diff_result.returncode != 0:
            return ResultError(ErrorStatus.INCORRECT_OUTPUT)
        return ResultOk()
