import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = "COMPTA"

COL_EMPLOYE_NAME = 2
COL_JUS = 6
HEADER_ROW = 6

def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

def load_start_time():
    try:
        with open("server/start_time.json", "r") as f:
            data = json.load(f)
            return datetime.fromisoformat(data["start_time"])
    except Exception as e:
        print(f"⚠️ Erreur de lecture start_time.json : {e}")
        return datetime.now()

def save_start_time(dt):
    os.makedirs("server", exist_ok=True)
    with open("server/start_time.json", "w") as f:
        json.dump({"start_time": dt.isoformat()}, f)

def reset_juice_column():
    sheet = get_sheet()
    names = sheet.col_values(COL_EMPLOYE_NAME)[HEADER_ROW:]
    for idx, _ in enumerate(names, start=HEADER_ROW + 1):
        sheet.update_cell(idx, COL_JUS, 0)
    print(f"🔁 {len(names)} lignes réinitialisées (colonne F)")

def update_juice_sales(sales_data):
    sheet = get_sheet()
    employee_names = sheet.col_values(2)

    for entry in sales_data:
        name = entry["name"].strip().lower()
        quantity = entry["quantity"]
        found = False

        for idx, cell_value in enumerate(employee_names, start=1):
            if cell_value.strip().lower() == name:
                try:
                    current_value = sheet.cell(idx, 6).value or "0"
                    current = int(str(current_value).replace(",", "").split(".")[0])
                except ValueError:
                    current = 0

                new_total = current + quantity
                sheet.update_cell(idx, 6, new_total)
                print(f"✅ {entry['name']} → {current} + {quantity} = {new_total} jus")
                found = True
                break

        if not found:
            print(f"❌ Aucun employé trouvé pour : {entry['name']}")
