const WEBHOOK_URL = "gsheets/webhook";

function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  const row = e.range.getRow();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const spreadsheetId = ss.getId();
  const sheetId = sheet.getSheetId();
  const sheetName = sheet.getName();

  if (row === 1) return; // пропускаем заголовки

  const values = sheet.getRange(row, 1, 1, sheet.getLastColumn()).getValues()[0];

  const payload = {
    row: row,
    spreadsheetId: spreadsheetId,
    sheetId: sheetId,
    sheetName: sheetName,
    data: values
  };

  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload)
  };

  UrlFetchApp.fetch(WEBHOOK_URL, options);
}


