from pathlib import Path
import os
import pandas as pd

try:
    os.getxattr
except AttributeError:
    raise ImportError("`os.getxattr` is not available on this platform. Use Linux.")


def get_drive_url(file: Path):
    id_drive = os.getxattr(file, "user.drive.id").decode()
    return f"https://drive.google.com/file/d/{id_drive}"


class WorkSheet:
    pass

    def create_page(self, name: str, df: pd.DataFrame):
        heet = gs_client.open_by_url(sheet_url)
        worksheet = wb.add_worksheet(name, rows=len(df), cols=len(df.columns))
        gspread_set_with_df(worksheet, df)
