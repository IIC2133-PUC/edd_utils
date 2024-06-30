from pathlib import Path
import subprocess
from subprocess import DEVNULL

from edd_utils.grader import Grader, GraderConfig
from edd_utils.runner import InputOutputRunner, ResultOk, ResultError, check_leaks_and_memory_errors

# COnfiguración del semestre


def get_columns_names(tests: list[str]):
    columns = ["user"]
    for test in tests:
        columns.append(f"{test} resultado")
        columns.append(f"{test} puntaje")
    columns.append("ok leaks")
    columns.append("ok mem_errors")
    return columns


grader_config = GraderConfig(github_org="IIC2133-PUC", get_columns_names=get_columns_names)


# Configuración de la evaluación


def compile(path: Path, optimize: bool = False):
    if optimize:
        subprocess.run(["sed", "-i", "s/OPT=-g/OPT=-O3/g", path / "Makefile"], check=True)
    compile_result = subprocess.run(["make"], cwd=path, stdout=DEVNULL, stderr=DEVNULL)
    return compile_result.returncode == 0


def clean(path: Path):
    subprocess.run(["make", "clean"], cwd=path, stdout=DEVNULL, stderr=DEVNULL)


def test_sorter(group: str, name: str):
    groups_values = {"nyctalus_search": 0, "trash": 1, "find_groups": 2}
    return groups_values[group], name


grader = Grader(
    assignment="T3-2024-1",
    dirs_name="T3",
    config=grader_config,
    test_sorter=test_sorter,
    submissions_path=Path("alumnos.tsv"),
)


runner = InputOutputRunner(timeout=10, mbs_limit=1024)

for submission in grader.submissions:
    if submission.has_run():
        continue

    last_test_that_worked = None

    submission.clone_or_pull()
    compile(submission.repo_path, optimize=False)

    for test in grader.tests:
        input_path = (test.path / "input.txt").resolve()
        output_path = (submission.repo_path / "output.txt").resolve()
        expected_output_path = (test.path / "output.txt").resolve()

        result = runner.run(test.group, input_path, output_path, expected_output_path, cwd=submission.repo_path)

        if isinstance(result, ResultOk):
            submission.save_result(f"{test} resultado", "OK")
            submission.save_result(f"{test} puntaje", "1")
            last_test_that_worked = [f"./{test.group}", input_path, output_path]

        elif isinstance(result, ResultError):
            submission.save_result(f"{test} resultado", result.status.value)
            submission.save_result(f"{test} puntaje", "0")

        output_path.unlink(missing_ok=True)

    if last_test_that_worked:
        valgrind_result = check_leaks_and_memory_errors(last_test_that_worked, cwd=submission.repo_path)
        if valgrind_result is not None:
            leaks_ok, mem_ok = valgrind_result
            submission.save_result("ok leaks", int(leaks_ok))
            submission.save_result("ok mem_errors", int(mem_ok))

    submission.save()
