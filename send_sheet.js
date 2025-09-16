function sendRowsToWebhook() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const data = sheet.getDataRange().getValues();

  const webhookUrl = "ССЫЛКА/webhook";

  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const payload = {
      row: i + 1,
      data: row
    };

    try {
      const options = {
        method: "post",
        contentType: "application/json",
        payload: JSON.stringify(payload),
        muteHttpExceptions: true
      };

      const response = UrlFetchApp.fetch(webhookUrl, options);
      Logger.log(`Row ${i+1} sent. Response: ${response.getResponseCode()} ${response.getContentText()}`);
    } catch (e) {
      Logger.log(`Error sending row ${i+1}: ${e}`);
    }
  }
}
