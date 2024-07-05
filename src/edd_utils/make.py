from pathlib import Path
import subprocess
from subprocess import DEVNULL


def build(path: Path):
    subprocess.run(["make"], cwd=path, stdout=DEVNULL, stderr=DEVNULL)


def clean(path: Path):
    subprocess.run(["make", "clean"], cwd=path, stdout=DEVNULL, stderr=DEVNULL)
