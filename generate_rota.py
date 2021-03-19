from datetime import datetime, timedelta
import os
import pickle
import random

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from settings import google_calendar_api, date_range, support_team


def weekday_dates(start_date: datetime, end_date: datetime) -> list:
    """Generates a list of dates excluding weekends between the date range provided.

    Parameters
    ----------
    start_date : datetime
    end_date : datetime

    Returns
    -------
    dates: list
    """
    dates = []
    for days_delta in range((end_date - start_date).days + 1):
        date = start_date + timedelta(days_delta)
        if date.weekday() not in [5, 6]:
            dates.append(date)
    return dates


def create_service(client_secret_file, api_name: str, api_version: str, scopes: list):
    """Creates a serive connection to the Google Calendar API.

    Parameters
    ----------
    client_secret_file
        The path to the client secrets file
    api_name : str
        The Google API to create a service for
    api_version : str
        The Google API version
    scopes : list
        The list of scopes to request during the flow

    Returns
    -------
    service
        A connection to the Google Calendar API
    """
    cred = None
    pickle_file = f"token_{api_name}_{api_version}.pickle"

    if os.path.exists(pickle_file):
        with open(pickle_file, "rb") as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
            cred = flow.run_local_server()

        with open(pickle_file, "wb") as token:
            pickle.dump(cred, token)

        try:
            service = build(api_name, api_version, credentials=cred)
            print(api_name, "service created successfully")
            return service
        except Exception as e:
            print(e)
            os.remove(pickle_file)
            return None


client_secret_file = google_calendar_api["client_secret_file"]
api_name = google_calendar_api["api_name"]
api_version = google_calendar_api["api_version"]
scopes = google_calendar_api["scopes"]
calendar_id = google_calendar_api["calendar_id"]
service = create_service(client_secret_file, api_name, api_version, scopes)
event = {}

start_date = datetime.strptime(date_range["start_date"], "%Y-%m-%d").date()
end_date = datetime.strptime(date_range["end_date"], "%Y-%m-%d").date()
weekday_dates = weekday_dates(start_date, end_date)

g_sevens = support_team["g_sevens"]
the_rest = support_team["the_rest"]
g_seven_leads = []
the_rest_leads = []
g_seven_index_splits = [len(g_sevens) - 1]
the_rest_index_splits = [(len(g_sevens) + len(the_rest)) - 1]
g_sevens_index = []
the_rest_index = []
support_pairs = {}

# Two lists of pairs leading support for the day (to be combined)
for i in range(len(weekday_dates)):
    g_seven_leads.append((g_sevens[i % len(g_sevens)], the_rest[i % len(the_rest)]))
    the_rest_leads.append((the_rest[i % len(the_rest)], g_sevens[i % len(g_sevens)]))
random.shuffle(g_seven_leads)
random.shuffle(the_rest_leads)

# Index values where support transistions from g_seven_leads to the_rest_leads
quotient = len(weekday_dates) // (len(g_sevens) + len(the_rest))
for i in range(2, quotient + 1):
    g_seven_index_splits.append(
        (i * (len(g_sevens) + len(the_rest)) - len(the_rest)) - 1
    )
    the_rest_index_splits.append((i * (len(g_sevens) + len(the_rest))) - 1)

# Index values for the respective "leads" lists
i = 0
while i <= len(weekday_dates):
    if i not in g_seven_index_splits:
        g_sevens_index.append(i)
        i += 1
    elif i not in the_rest_index_splits:
        g_sevens_index.append(i)
        i += len(the_rest) + 1

i = len(g_sevens) - 1
while i <= len(weekday_dates):
    if i not in the_rest_index_splits:
        i += 1
        the_rest_index.append(i)
    elif i not in g_seven_index_splits:
        i += len(g_sevens) + 1
        the_rest_index.append(i)

# combine "leads" lists to give final pairs
for i in range(len(g_sevens_index[: len(weekday_dates)])):
    support_pairs[g_sevens_index[i]] = g_seven_leads[i]
for i in range(len(the_rest_index[: len(weekday_dates)])):
    support_pairs[the_rest_index[i]] = the_rest_leads[i]

# delete all events from calendar
page_token = None
while True:
    events = (
        service.events().list(calendarId=calendar_id, pageToken=page_token,).execute()
    )
    for event in events["items"]:
        if datetime.strptime(event["start"]["date"], "%Y-%m-%d").date() >= start_date:
            service.events().delete(
                calendarId=calendar_id, eventId=event["id"]
            ).execute()
    page_token = events.get("nextPageToken")
    if not page_token:
        break

# populate calendar with events
for i in range(len(weekday_dates)):
    event["summary"] = (
        f"{support_pairs[i][0]} is on support today with {support_pairs[i][1]} "
        "assisting"
    )
    event["start"] = {"date": str(weekday_dates[i])}
    event["end"] = {"date": str(weekday_dates[i])}
    service.events().insert(calendarId=calendar_id, body=event).execute()
