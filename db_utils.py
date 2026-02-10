import json
import gspread
import pandas as pd
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials


# -----------------------------------
# GOOGLE SHEET CONFIG
# -----------------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1hwcBQkniPfC_YEsw7Bpi_fLSC-AB7EVmRUOJ2vXEjlo/edit#gid=0"

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]


# -----------------------------------
# CREATE GOOGLE CLIENT FROM SECRETS
# -----------------------------------
def get_client():
    """
    Authenticate using service account JSON stored in Streamlit Secrets.
    """
    service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"])

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        service_account_info,
        SCOPE
    )

    client = gspread.authorize(creds)
    return client


# -----------------------------------
# FETCH DATA FROM GOOGLE SHEET
# -----------------------------------
def fetch_data(sheet_name):
    """
    Loads a worksheet into a pandas DataFrame.
    """
    try:
        client = get_client()
        sheet = client.open_by_url(SHEET_URL).worksheet(sheet_name)
        data = sheet.get_all_records()
        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"Error loading sheet '{sheet_name}': {e}")
        return pd.DataFrame()
