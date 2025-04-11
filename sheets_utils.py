import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Feuille 1")
    return sheet

def load_start_time():
    try:
        with open("server/start_time.json", "r") as f:
            data = json.load(f)
            return datetime.fromisoformat(data["start_time"])
    except:
        return datetime.now()

def save_start_time(dt):
    with open("server/start_time.json", "w") as f:
        json.dump({"start_time": dt.isoformat()}, f)

def reset_juice_column():
    sheet = get_sheet()
    names = sheet.col_values(2)[1:]
    for idx, _ in enumerate(names, start=2):
        sheet.update_cell(idx, 6, 0)

def update_juice_sales(sales_data):
    sheet = get_sheet()
    records = sheet.get_all_records()
    for entry in sales_data:
        name = entry["name"]
        quantity = entry["quantity"]
        for idx, row in enumerate(records, start=2):
            if row["Nom et Prénom Employé"].strip().lower() == name.strip().lower():
                current = int(sheet.cell(idx, 6).value or 0)
                sheet.update_cell(idx, 6, current + quantity)
                break
