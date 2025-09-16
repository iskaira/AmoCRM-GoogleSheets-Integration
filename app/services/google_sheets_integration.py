from app.external_api.google_sheets import GoogleSheetsClient


class GoogleSheetsService:
    def __init__(self, client: GoogleSheetsClient, spreadsheet_id: str, sheet_name: str):
        self.client = client
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name

    def update_user_by_key(self, key_value: str, updates: dict[str, str]) -> bool:
        ws = self.client.get_worksheet(self.spreadsheet_id, self.sheet_name)
        row = self.client.find_row_by_col_value(ws, 5, key_value)
        if not row:
            return False

        # маппинг: название -> индекс
        columns_map = {
            "Email": 2,
            "Phone": 1,
            "price": 3,
            "Comment": 4,
            "status_id": 6,
        }
        mapped = {columns_map[k]: v for k, v in updates.items() if k in columns_map}
        self.client.update_cells(ws, row, mapped)
        return True

    def set_lead_status_for_row(self, row_number: int, lead_id: str, status_id: str):
        ws = self.client.get_worksheet(self.spreadsheet_id, self.sheet_name)
        updates = {
            5: lead_id,   # 5-я колонка lead
            6: status_id,  # 6-я колонка status
        }
        self.client.update_cells(ws, row_number, updates)

