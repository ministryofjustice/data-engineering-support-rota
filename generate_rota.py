from datetime import datetime, timedelta
import os
import random
from typing import Union

from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_core import retry
from googleapiclient.discovery import build, Resource
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from settings import google_calendar_api, date_range, support_team

if support_team["start_cycle_with"] not in ["g_sevens", "everyone_else"]:
    raise ValueError(f"{support_team['start_cycle_with']} is an invalid group name.")


def string_to_datetime(date: str) -> datetime:
    """Takes a date as a sting of the format YYYY-MM-DD and converts it to a datetime
    object.
    """
    return datetime.strptime(date, "%Y-%m-%d").date()


def get_workday_dates(start_date: datetime, n_days: int) -> list:
    """Generates a list of dates excluding weekends between the date range provided."""
    dates = []
    days_delta = 0

    while len(dates) != n_days:
        date = start_date + timedelta(days_delta)
        days_delta += 1
        if date.weekday() not in [5, 6]:
            dates.append(date)

    return dates


def generate_support_pairs(group_one: list, group_two: list, n_days: int) -> list:
    """Generates a list of 2-tuples containing a leading and assisting pair to work
    support.
    """
    group_one_long = []
    while len(group_one_long) < n_days:
        group_one_long.extend(group_one)
        # group_one.append(group_one.pop(0))

    group_two_long = []
    while len(group_two_long) < n_days:
        group_two_long.extend(group_two)
        # group_two.append(group_two.pop(0))

    support_pairs_preprocessing = []
    support_pairs = []

    for i in range(n_days):
        support_pairs_preprocessing.append((group_one_long[i], group_two_long[i]))

    index = 0
    for i in range(date_range["n_cycles"]):
        for j in range(len(group_one)):
            support_pairs.append(support_pairs_preprocessing[index])
            index += 1
        for k in range(len(group_two)):
            support_pairs.append(
                (
                    support_pairs_preprocessing[index][1],
                    support_pairs_preprocessing[index][0],
                )
            )
            index += 1

    return support_pairs


def create_service(
    client_secret_file: str, api_name: str, api_version: str, scopes: list
) -> Resource:
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
    creds = None
    token_file = f"{api_name}_api_{api_version}_token.json"

    if os.path.exists(token_file):
        print("Reading token...")
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Refreshing token...")
                creds.refresh(Request())
            except Exception:
                print("Couldn't refresh token, trying to get a new one...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_file, scopes
                )
                creds = flow.run_local_server(port=0)
        else:
            print("Getting token...")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
            creds = flow.run_local_server(port=0)

        print("Writing updated token to file...")
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    service = build(serviceName=api_name, version=api_version, credentials=creds)
    print(api_name.capitalize(), "API service created successfully.")

    return service


@retry.Retry()
def get_list_events_response(
    service: Resource, calendar_id: str, page_token: Union[str, None], start_date: str
) -> dict:
    return (
        service.events()
        .list(
            calendarId=calendar_id,
            pageToken=page_token,
            timeMin=start_date + "T00:00:00.000000Z",
        )
        .execute()
    )


@retry.Retry()
def delete_calendar_event(service: Resource, calendar_id: str, event_id: str):
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()


@retry.Retry()
def write_calendar_event(service: Resource, calendar_id: str, event_body: dict):
    service.events().insert(calendarId=calendar_id, body=event_body).execute()


service = create_service(
    google_calendar_api["client_secret_file"],
    google_calendar_api["api_name"],
    google_calendar_api["api_version"],
    google_calendar_api["scopes"],
)
calendar_id = google_calendar_api["calendar_id"]["prod"]

g_sevens = support_team["g_sevens"]
random.shuffle(g_sevens)
everyone_else = support_team["everyone_else"]
random.shuffle(everyone_else)

start_date = string_to_datetime(date_range["start_date"])
n_days = date_range["n_cycles"] * (len(g_sevens) + len(everyone_else))
workday_dates = get_workday_dates(start_date, n_days)
end_date = workday_dates[-1]

if support_team["start_cycle_with"] == "g_sevens":
    support_pairs = generate_support_pairs(
        group_one=g_sevens, group_two=everyone_else, n_days=n_days
    )
else:
    support_pairs = generate_support_pairs(
        group_one=everyone_else, group_two=g_sevens, n_days=n_days
    )


print(f"Deleting all calendar events from {date_range['start_date']} onwards...")
page_token = None
while True:
    response = get_list_events_response(
        service, calendar_id, page_token, date_range["start_date"]
    )
    events = response.get("items", [])
    for event in events:
        delete_calendar_event(service, calendar_id, event["id"])
    page_token = response.get("nextPageToken", None)
    if not page_token:
        break

event_body = {}
print("Writing rota to calendar...")
for i in range(n_days):
    event_body["summary"] = (
        f"{support_pairs[i][0]} is on support today with {support_pairs[i][1]} "
        "assisting"
    )
    event_body["start"] = {"date": str(workday_dates[i])}
    event_body["end"] = {"date": str(workday_dates[i])}
    write_calendar_event(service, calendar_id, event_body)

everyone = list(g_sevens)
everyone.extend(everyone_else)

print(f"\nIn {n_days} working days:")
for individual in everyone:
    count = 0
    for pair in support_pairs:
        if individual in pair:
            count += 1
    print(f"{individual} has been scheduled to work support {count} times.")
