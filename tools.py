from db_utils import fetch_data, get_client, SHEET_URL
from datetime import datetime
import re

# -----------------------------
# Normalize column names
# -----------------------------
def normalize(df):
    df.columns = [c.lower().strip() for c in df.columns]
    return df


# -----------------------------
# GET PILOT ROSTER
# -----------------------------
def get_pilot_roster(filter_skill=None, only_available=False):
    df = fetch_data("Pilots")
    df = normalize(df)

    # availability filter ONLY when explicitly asked
    if only_available:
        df = df[df['status'].str.lower() == 'available']

    # skill filter
    if filter_skill:
        df = df[df['skills'].str.contains(filter_skill, case=False, na=False)]

    if df.empty:
        return "No matching pilots found."

    # RETURN DATAFRAME (not text)
    return df[['pilot_id','name','skills','location','status']]




# -----------------------------
# CHECK CONFLICTS
# -----------------------------
def check_conflicts(pilot_id, date_check):

    pilots = fetch_data("Pilots")
    pilots = normalize(pilots)

    pilot = pilots[pilots['pilot_id'] == pilot_id]

    if pilot.empty:
        return "Pilot not found."

    if pilot.iloc[0]['status'].lower() == 'on leave':
        return "CONFLICT: Pilot is On Leave."

    if pilot.iloc[0]['status'].lower() == 'assigned':
        return f"CONFLICT: Pilot assigned to {pilot.iloc[0]['current_assignment']}"

    return "No conflicts. Pilot is free."


# -----------------------------
# UPDATE STATUS
# -----------------------------
def update_pilot_status(pilot_id, new_status):

    client = get_client()
    sheet = client.open_by_url(SHEET_URL).worksheet("Pilots")

    cell = sheet.find(pilot_id)

    if not cell:
        return "Pilot ID not found."

    # status column is F (6)
    sheet.update_cell(cell.row, 6, new_status)

    return f"Updated {pilot_id} to {new_status}"
