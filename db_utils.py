import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

SHEET_URL = "https://docs.google.com/spreadsheets/d/1hwcBQkniPfC_YEsw7Bpi_fLSC-AB7EVmRUOJ2vXEjlo/edit?gid=0#gid=0"

import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)
    return client
)

def fetch_data(sheet_name):
    client = get_client()
    sheet = client.open_by_url(SHEET_URL).worksheet(sheet_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)
