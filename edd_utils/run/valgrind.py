from subprocess import run, DEVNULL, PIPE


from .types import CMD, StrOrBytesPath


def check_leaks_and_memory_errors(args: CMD, *, cwd: StrOrBytesPath | None = None) -> tuple[bool, bool] | None:
    "Returns the tuple (leaks_ok, mem_ok) where both are booleans or None if valgrind is not available."
    # Check if valgrind can be executed
    try:
        run(["valgrind", "--version"], stdout=DEVNULL, stderr=DEVNULL)
    except FileNotFoundError:
        return None

    valgrind_args = ["valgrind", *args]
    valgrind_output = run(valgrind_args, cwd=cwd, text=True, stdout=DEVNULL, stderr=PIPE)

    if "All heap blocks were freed -- no leaks are possible" in valgrind_output.stderr:
        leaks_ok = True
    if "ERROR SUMMARY: 0 errors from 0 contexts" in valgrind_output.stderr:
        mem_ok = True

    return leaks_ok, mem_ok
