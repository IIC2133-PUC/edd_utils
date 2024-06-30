from getpass import getpass
import subprocess
from subprocess import PIPE


def authenticate(*, help=True):
    if help:
        print("Create a token at https://github.com/settings/tokens?type=beta")
        print("The token must have:")
        print("  - Resource owner: The organization that owns the classroom")
        print("  - Repository access: All repositories")
        print("  - Repository permissions: Contents (read-only)")

    github_secret_token = getpass(prompt="GitHub PAT: ")
    gh_cli_args = ["gh", "auth", "login", "--hostname", "github.com", "--git-protocol", "https", "--with-token"]
    process = subprocess.Popen(gh_cli_args, stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)
    stdout, stderr = process.communicate(input=github_secret_token)

    process.wait()
    if process.returncode != 0 or subprocess.run(["gh", "auth", "status"], stdout=PIPE).returncode != 0:
        raise Exception(f"GitHub authentication failed:\n{stdout}{stderr}")

    # Install GitHub Classroom CLI (can't be installed before authentication)
    subprocess.run(["gh", "extension", "install", "github/gh-classroom"], check=True)


def clone_assignments(assignment_id: int):
    subprocess.run(["gh", "classroom", "clone", "student-repos", "--assignment-id", str(assignment_id)], check=True)
