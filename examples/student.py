from pathlib import Path
import subprocess

from edd_utils.tests import get_sorted_tests
from edd_utils.run import InputOutputRunner, ResultOk, ResultError, check_leaks_and_memory_errors
from edd_utils import make


def compile(path: Path, optimize: bool = False):
    if optimize:
        subprocess.run(["sed", "-i", "s/OPT=-g/OPT=-O3/g", path / "Makefile"], check=True)
    make.build(path)


def test_sorter(group: str, name: str):
    groups_values = {"nyctalus_search": 0, "trash": 1, "find_groups": 2}
    return groups_values[group], name


runner = InputOutputRunner(timeout=10, mbs_limit=1024)
this_dir = Path.cwd()

tests = get_sorted_tests(this_dir / "tests")


compile(this_dir)

for test in tests:
    input_path = (test.path / "input.txt").resolve()
    output_path = (this_dir / "output.txt").resolve()
    expected_output_path = (test.path / "output.txt").resolve()

    result = runner.run(test.group, input_path, output_path, expected_output_path, cwd=this_dir)

    if isinstance(result, ResultOk):
        print(f"{test} resultado: OK")
        last_test_that_worked = [f"./{test.group}", input_path, output_path]

    elif isinstance(result, ResultError):
        print(f"{test} resultado: {result.status.value}")

    output_path.unlink(missing_ok=True)

if last_test_that_worked:
    try:
        leaks_ok, mem_ok = check_leaks_and_memory_errors(last_test_that_worked, cwd=this_dir)
        print(f"Leak check: {leaks_ok}")
        print(f"Memory check: {mem_ok}")
    except Exception as e:
        print(f"Error in leak check: {e}")
else:
    print("No tests passed")

make.clean(this_dir)
