import os
from pathlib import Path
from subprocess import run, DEVNULL


def clone(repos_path: Path, repo_name: str):
    run(["gh", "repo", "clone", repo_name], cwd=repos_path, check=True, stdout=DEVNULL, stderr=DEVNULL)


def fetch(repo_path: Path):
    run(["git", "fetch", "origin", "--prune", "--force"], cwd=repo_path, check=True, stdout=DEVNULL)


def reset(repo_path: Path, *, branch: str = "origin/main"):
    run(["git", "reset", "--hard", branch], cwd=repo_path, check=True, stdout=DEVNULL, stderr=DEVNULL)


def checkout(repo_path: Path, commit: str):
    run(["git", "checkout", commit], cwd=repo_path, check=True, stdout=DEVNULL, stderr=DEVNULL)


def last_commit(repo_path: Path, *, timezone: str = "America/Santiago"):
    "Returns a tuple of (commit_hash, commit_date)"
    env = os.environ.copy()
    env["TZ"] = timezone
    args = ["git", "log", "-1", "--date=format-local:%Y-%m-%d %H:%M:%S", "--format=%H %cd"]
    process = run(args, cwd=repo_path, env=env, capture_output=True, text=True)
    commit_data = process.stdout.strip()
    if process.returncode != 0 or not commit_data:
        return None, None
    return commit_data.split(" ", maxsplit=1)
