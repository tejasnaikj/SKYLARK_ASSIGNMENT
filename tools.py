from langchain.tools import tool
from db_utils import fetch_data, get_client, SHEET_URL
import pandas as pd
from datetime import datetime

@tool
def get_pilot_roster(filter_skill: str = None):
    """
    Returns the list of pilots. 
    Use this to check who is available or what skills they have.
    """
    df = fetch_data("Pilots")
    if filter_skill:
        df = df[df['skills'].str.contains(filter_skill, case=False, na=False)]
    return df.to_markdown(index=False)

@tool
def check_conflicts(pilot_id: str, date_check: str):
    """
    Checks if a pilot is free on a specific date.
    date_check format: 'YYYY-MM-DD'
    """
    # Check if pilot exists/is on leave
    pilots = fetch_data("Pilots")
    pilot = pilots[pilots['id'] == pilot_id]
    if pilot.empty: return "Pilot not found."
    if pilot.iloc[0]['status'] == 'On Leave': return "CONFLICT: Pilot is On Leave."

    # Check missions
    missions = fetch_data("Missions")
    pilot_missions = missions[missions['assigned_pilot_id'] == pilot_id]

    check_dt = datetime.strptime(date_check, "%Y-%m-%d")

    for _, m in pilot_missions.iterrows():
        start = datetime.strptime(m['start_date'], "%Y-%m-%d")
        end = datetime.strptime(m['end_date'], "%Y-%m-%d")
        if start <= check_dt <= end:
            return f"CONFLICT: Pilot assigned to Mission {m['id']}"

    return "No conflicts. Pilot is free."

@tool
def update_pilot_status(pilot_id: str, new_status: str):
    """
    Updates a pilot's status (Available, On Leave, Assigned).
    Only use this if the user explicitly asks to change status.
    """
    client = get_client()
    sheet = client.open_by_url(SHEET_URL).worksheet("Pilots")

    cell = sheet.find(pilot_id)
    if not cell: return "Pilot ID not found."

    # Status is column 5 (E)
    sheet.update_cell(cell.row, 5, new_status) 
    return f"Updated {pilot_id} to {new_status}"
    