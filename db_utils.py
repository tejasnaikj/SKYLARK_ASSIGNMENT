import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# Constants
# REPLACE THIS WITH YOUR ACTUAL GOOGLE SHEET URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1hwcBQkniPfC_YEsw7Bpi_fLSC-AB7EVmRUOJ2vXEjlo/edit?gid=1229153156#gid=1229153156"

def get_client():
    # We use st.secrets for cloud deployment, but fallback to local json for testing
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    try:
        # Try loading from Streamlit secrets (Production)
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    except:
        # Fallback to local file (Local Development)
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)

    return gspread.authorize(creds)

def fetch_data(sheet_name):
    client = get_client()
    sheet = client.open_by_url(SHEET_URL).worksheet(sheet_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)
