from subprocess import run, DEVNULL, PIPE


from .types import CMD, StrOrBytesPath


def check_leaks_and_memory_errors(args: CMD, *, cwd: StrOrBytesPath | None = None) -> tuple[bool, bool]:
    "Returns the tuple (leaks_ok, mem_ok) where both are booleans or None if valgrind is not available."
    # Check if valgrind can be executed
    run(["valgrind", "--version"], stdout=DEVNULL, stderr=DEVNULL)

    valgrind_args = ["valgrind", *args]
    valgrind_output = run(valgrind_args, cwd=cwd, text=True, stdout=DEVNULL, stderr=PIPE)

    leaks_ok = "All heap blocks were freed -- no leaks are possible" in valgrind_output.stderr:
    mem_ok = "ERROR SUMMARY: 0 errors from 0 contexts" in valgrind_output.stderr

    return leaks_ok, mem_ok
