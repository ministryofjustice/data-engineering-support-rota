from datetime import datetime, timedelta
import os
import random

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from settings import google_calendar_api, date_range, support_team


def string_to_datetime(date: str) -> datetime:
    """Takes a date as a sting of the format YYYY-MM-DD and converts it to a datetime
    object.
    """
    return datetime.strptime(date, "%Y-%m-%d").date()


def get_workday_dates(start_date: datetime, n_days: int) -> list:
    """Generates a list of dates excluding weekends between the date range provided.

    Parameters
    ----------
    start_date : datetime
    n_days: int

    Returns
    -------
    list
    """
    dates = []
    days_delta = 0

    while len(dates) != n_days:
        date = start_date + timedelta(days_delta)
        days_delta += 1
        if date.weekday() not in [5, 6]:
            dates.append(date)

    return dates


def repeat_and_shuffle_without_consecutive_elements(
    input_list: list, n_repeats: int
) -> list:
    """Repeats a list the given number of times and shuffles its elements whilst
    ensuring no two consecutive values are equal.

    Parameters
    ----------
    input_list : list
        The list you want to repeat and shuffle.
    n_repeats : int
        The number of times you want to repeat the input list.

    Returns
    -------
    list
        A list of length n_repeats * len(input_list), shuffled with no two consecutive
        values being equal.

    Raises
    ------
    ValueError
        If the input list contains duplicate values.
    """

    if len(set(input_list)) != len(input_list):
        raise ValueError("Remove the duplicate value in this list: ", input_list)

    output = list(input_list)
    random.shuffle(output)

    for i in range(n_repeats - 1):
        shuffle_list = [element for element in input_list if element not in output[-1]]
        random.shuffle(shuffle_list)
        shuffle_list.append(output[-1])
        shuffle_list[1:] = random.sample(shuffle_list[1:], len(shuffle_list) - 1)
        output.extend(shuffle_list)

    return output


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
    creds = None
    pickle_file = f"{api_name}_api_{api_version}_token.json"

    if os.path.exists(pickle_file):
        print("Reading token...")
        creds = Credentials.from_authorized_user_file(pickle_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing token...")
            creds.refresh(Request())
        else:
            print("Getting token...")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
            creds = flow.run_local_server(port=0)

        with open(pickle_file, "w") as token:
            print("Writing updated token to file...")
            token.write(creds.to_json())

    try:
        service = build(serviceName=api_name, version=api_version, credentials=creds)
        print(api_name.capitalize(), "API service created successfully")
        return service
    except Exception as error:
        print(error)
        return None


service = create_service(
    google_calendar_api["client_secret_file"],
    google_calendar_api["api_name"],
    google_calendar_api["api_version"],
    google_calendar_api["scopes"],
)
calendar_id = google_calendar_api["calendar_id"]
event_body = {}

g_sevens = support_team["g_sevens"]
everyone_else = support_team["everyone_else"]
support_pairs = []

start_date = string_to_datetime(date_range["start_date"])
n_days = date_range["n_cycles"] * (len(g_sevens) + len(everyone_else))
workday_dates = get_workday_dates(start_date, n_days)
end_date = workday_dates[-1]

g_sevens_shuffled = repeat_and_shuffle_without_consecutive_elements(
    input_list=g_sevens, n_repeats=(len(workday_dates) // len(g_sevens)) + 1
)
everyone_else_shuffled = repeat_and_shuffle_without_consecutive_elements(
    input_list=everyone_else, n_repeats=(len(workday_dates) // len(everyone_else)) + 1
)

index = None
for i in range(date_range["n_cycles"]):
    for j in range(len(g_sevens)):
        if index is None:
            index = 0
        else:
            index += 1
        support_pairs.append((g_sevens_shuffled[index], everyone_else_shuffled[index]))

    for k in range(len(everyone_else)):
        index += 1
        support_pairs.append((everyone_else_shuffled[index], g_sevens_shuffled[index]))

# Delete events from calendar
page_token = None
while True:
    response = (
        service.events()
        .list(
            calendarId=calendar_id,
            pageToken=page_token,
            timeMin=date_range["start_date"] + "T00:00:00.000000Z",
        )
        .execute()
    )
    events = response.get("items", [])

    for event in events:
        print(f"Deleting calendar event id: {event['id']}")
        service.events().delete(calendarId=calendar_id, eventId=event["id"]).execute()
    page_token = response.get("nextPageToken", None)

    if not page_token:
        break

# Populate calendar with events
for i in range(n_days):
    event_body["summary"] = (
        f"{support_pairs[i][0]} is on support today with {support_pairs[i][1]} "
        "assisting"
    )
    event_body["start"] = {"date": str(workday_dates[i])}
    event_body["end"] = {"date": str(workday_dates[i])}
    service.events().insert(calendarId=calendar_id, body=event_body).execute()

everyone = list(g_sevens)
everyone.extend(everyone_else)

for individual in everyone:
    count = 0
    for pair in support_pairs:
        if individual in pair:
            count += 1
    print(f"{individual} has been scheduled to work support {count} times.")
