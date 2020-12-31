from datetime import datetime, timedelta
import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


def next_weekday(date, weekday: int):
    """Returns the next date of a given weekday.

    Parameters
    ----------
    date : datetime
        The date from which you want get the date of the next occurance of a particular
        day of the week.
    weekday : int
        The weekday you want the next occuring date for.

    Returns
    -------
    datetime
        The date of the next occurance of a particular day of the week from the given
        date.
    """
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0:  # if the target day has already happened this week
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)


def weekday_dates(start_date: datetime, end_date: datetime) -> list:
    """Generates a list of dates excluding weekends between the date range provided.

    Parameters
    ----------
    start_date : datetime
    end_date : datetime

    Returns
    -------
    list
        [description]
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
        return None


client_secret_file = "data_engineering_support_rota_creds.json"
api_name = "calendar"
api_version = "v3"
scopes = ["https://www.googleapis.com/auth/calendar"]

service = create_service(client_secret_file, api_name, api_version, scopes)
calendar = (
    service.events()
    .list(calendarId="9c720gjf06r8odu2vhsfvd7e9k@group.calendar.google.com")
    .execute()
)
for item in calendar["items"]:
    service.events().delete(
        calendarId="9c720gjf06r8odu2vhsfvd7e9k@group.calendar.google.com",
        eventId=item["id"],
    ).execute()
