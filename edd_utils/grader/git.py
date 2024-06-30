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
