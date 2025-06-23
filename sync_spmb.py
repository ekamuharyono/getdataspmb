import pandas as pd
from bs4 import BeautifulSoup
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from io import StringIO

# === Setup credentials ===
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service_account.json", scopes=scopes)
gc = gspread.authorize(creds)

# === Baca file HTML ===
with open("spmb.html", "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")
h4s = soup.find_all("h4")
jurusan_headers = [h4.get_text(strip=True) for h4 in h4s[1:]]
tables = pd.read_html(StringIO(html_content))
print(f"Jumlah tabel: {len(tables)}")

# === Buka Google Sheets ===
spreadsheet_id = "1N8KHa7SfU-r228FGm3kvK8hK7hVJ2d0_gZ3h0V43NxI"
spreadsheet = gc.open_by_key(spreadsheet_id)

# === Hapus semua kecuali 1 sheet ===
worksheets = spreadsheet.worksheets()
if len(worksheets) > 1:
    for ws in worksheets[:-1]:
        spreadsheet.del_worksheet(ws)

# === Isi sheet pertama ===
ws = spreadsheet.worksheets()[0]
ws.update_title(jurusan_headers[0][:100])
ws.clear()

df = tables[0]
if 'Nomor Pendaftaran' in df.columns[0]:
    df = df.drop(df.columns[0], axis=1)
set_with_dataframe(ws, df)

# === Sisanya ===
for i in range(1, len(tables)):
    sheet_name = jurusan_headers[i][:100] if i < len(jurusan_headers) else f"Jurusan_{i+1}"
    df = tables[i]
    if 'Nomor Pendaftaran' in df.columns[0]:
        df = df.drop(df.columns[0], axis=1)
    ws_new = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
    set_with_dataframe(ws_new, df)

print("✅ Selesai update Google Sheets!")
