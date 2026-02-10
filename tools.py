from db_utils import fetch_data, get_client, SHEET_URL
import pandas as pd

# Normalize columns
def normalize(df):
    df.columns = [c.lower().strip() for c in df.columns]
    return df


# -----------------------------
# TOOL 1 — Pilot roster
# -----------------------------
def get_pilot_roster(skill=None, only_available=False):
    df = fetch_data("Pilots")
    df = normalize(df)

    if only_available:
        df = df[df['status'].str.lower() == 'available']

    if skill:
        df = df[df['skills'].str.contains(skill, case=False, na=False)]

    if df.empty:
        return "No matching pilots found."

    return df[['pilot_id','name','skills','location','status']].to_dict(orient="records")


# -----------------------------
# TOOL 2 — Conflict check
# -----------------------------
def check_conflicts(pilot_id, date=None):
    pilots = fetch_data("Pilots")
    pilots = normalize(pilots)

    pilot = pilots[pilots['pilot_id'] == pilot_id]

    if pilot.empty:
        return "Pilot not found."

    status = pilot.iloc[0]['status'].lower()

    if status == 'on leave':
        return "CONFLICT: Pilot is on leave."

    if status == 'assigned':
        return f"CONFLICT: Assigned to {pilot.iloc[0]['current_assignment']}"

    return "No conflicts. Pilot available."


# -----------------------------
# TOOL 3 — Update status
# -----------------------------
def update_pilot_status(pilot_id, status):
    client = get_client()
    sheet = client.open_by_url(SHEET_URL).worksheet("Pilots")

    cell = sheet.find(pilot_id)

    if not cell:
        return "Pilot ID not found."

    sheet.update_cell(cell.row, 6, status)
    return f"{pilot_id} updated to {status}"
