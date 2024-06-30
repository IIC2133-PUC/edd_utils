import gspread
import gspread_dataframe
import pandas as pd

from google.auth.credentials import Credentials


class SpreadSheetClient:
    def __init__(self, credentials: Credentials, sheet_key: str):
        self.client = gspread.authorize(credentials)  # type: ignore
        self.sheet_key = sheet_key
        self.sheet = self.client.open_by_key(self.sheet_key)

    def save_sheet(self, title: str, df: pd.DataFrame, *, overwrite: bool = False):
        try:
            sheet = self.sheet.add_worksheet(title, df.shape[0], df.shape[1])
        except gspread.exceptions.APIError:
            if overwrite:
                sheet = self.sheet.worksheet(title)
                sheet.clear()
            else:
                raise ValueError(f"Worksheet {title} already exists. Use `overwrite=True` to overwrite it.")
        gspread_dataframe.set_with_dataframe(sheet, df)

    def get_sheet(self, title: str):
        sheet = self.sheet.worksheet(title)
        data = sheet.get_values()
        return pd.DataFrame(data[1:], columns=data[0])
