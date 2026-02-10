import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

SHEET_URL = "https://docs.google.com/spreadsheets/d/1hwcBQkniPfC_YEsw7Bpi_fLSC-AB7EVmRUOJ2vXEjlo/edit?gid=0#gid=0"

def get_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    except:
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)

    return gspread.authorize(creds)

def fetch_data(sheet_name):
    client = get_client()
    sheet = client.open_by_url(SHEET_URL).worksheet(sheet_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)
