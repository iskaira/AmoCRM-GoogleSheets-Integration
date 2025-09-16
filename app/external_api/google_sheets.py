from typing import Optional
from app.constants import GOOGLE_SERVICE_ACCOUNT_FILE

import pygsheets


class GoogleSheetsClient:
    def __init__(self):
        self.client = pygsheets.authorize(service_account_file=GOOGLE_SERVICE_ACCOUNT_FILE,
                                          check=False)

    def get_worksheet(self, spreadsheet_id: str, sheet_name: str):
        sh = self.client.open_by_key(spreadsheet_id)
        return sh.worksheet_by_title(sheet_name)

    def find_row_by_col_value(self, ws, col: int, value: str) -> Optional[int]:
        cell = ws.find(value, matchEntireCell=True, cols=(col, col))
        return cell[0].row if cell else None

    def update_cells(self, ws, row: int, updates: dict[int, str]) -> None:
        for col, val in updates.items():
            ws.update_value((row, col), val)
