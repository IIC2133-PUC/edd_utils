from pathlib import Path
import os


try:
    os.getxattr
except AttributeError:
    raise ImportError("`os.getxattr` is not available on this platform. Use Linux.")


def get_drive_url(file: Path):
    id_drive = os.getxattr(file, "user.drive.id").decode()
    return f"https://drive.google.com/file/d/{id_drive}"
