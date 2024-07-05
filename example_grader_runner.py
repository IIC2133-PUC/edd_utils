from pathlib import Path
import subprocess
from subprocess import DEVNULL

from edd_utils.grade import Grader, GraderConfig, Submission
from edd_utils.run import InputOutputRunner, ResultOk, ResultError, check_leaks_and_memory_errors
from edd_utils.tests import Test


def fill(submission: Submission, tests: list[Test], *, error: str):
    for test in tests:
        submission.save_result(f"{test} resultado", "0")
        submission.save_result(f"{test} puntaje", "0")


# Configuración del semestre


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


grader = Grader(assignment="T3-2024-1", dirs_name="T3", test_sorter=test_sorter, config=grader_config)
grader.load_submissions(Path("submissions.tsv"))

runner = InputOutputRunner(timeout=10, mbs_limit=1024)

for submission in grader.submissions:
    if submission.is_saved():
        continue

    last_test_that_worked = None

    try:
        submission.clone_or_pull()
    except Exception as e:
        print(f"Error al clonar/pull: {e}")
        fill(submission, grader.tests, error="CLONE ERROR")
        continue

    compile_ok = compile(submission.repo_path, optimize=False)
    if not compile_ok:
        fill(submission, grader.tests, error="COMPILE ERROR")
        continue

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
        try:
            leaks_ok, mem_ok = check_leaks_and_memory_errors(last_test_that_worked, cwd=submission.repo_path)
            submission.save_result("ok leaks", int(leaks_ok))
            submission.save_result("ok mem_errors", int(mem_ok))
        except Exception as e:
            print(f"Error al revisar leaks y memory errors de {submission.user}")

    submission.save()
