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


def string_to_datetime(date: str) -> datetime:
    """Takes a date as a sting of the format YYYY-MM-DD and converts it to a datetime
    object.
    """
    return datetime.strptime(date, "%Y-%m-%d").date()


def get_workday_dates(start_date: datetime, n_days: int) -> list:
    """Generates a list of dates excluding weekends that is n_days long starting at
    start_date.
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
    """Repeats a list the specified number of times and shuffles it's elements whilst
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

    for n in range(n_repeats - 1):
        shuffle_list = [element for element in input_list if element not in output[-1]]
        random.shuffle(shuffle_list)
        shuffle_list.append(output[-1])
        shuffle_list[1:] = random.sample(shuffle_list[1:], len(shuffle_list) - 1)
        output.extend(shuffle_list)

    return output


def generate_lead_list(group: list, n_cycles: int) -> list:
    """A helper function that repeats the list group for n_cycles and shuffles each
    repitition.
    """
    random.shuffle(group)
    repeat_and_shuffle = []

    for n in range(n_cycles):
        repeat_and_shuffle.extend(group)

    return repeat_and_shuffle


def generate_assist_list(group_a: list, group_b: list, n_cycles: int) -> list:
    """A helper function that takes group_a and repeats it the number of times required
    such that it's length is at least as long as the length of group_b * n_cycles. Each
    repitition is shuffled whilst ensuring no two consequtive elements are the same.
    Finally the repeated and shuffled group_a list is sliced to the exact length of
    group_b * n_cycles.
    """
    group_a_length = len(group_a)
    group_b_length = len(group_b)

    if group_a_length == group_b_length:
        return repeat_and_shuffle_without_consecutive_elements(group_a, n_cycles)

    elif group_a_length > group_b_length:
        return repeat_and_shuffle_without_consecutive_elements(
            group_a, ((group_b_length * n_cycles) // group_a_length) + 1
        )[: group_b_length * n_cycles]

    else:
        return repeat_and_shuffle_without_consecutive_elements(
            group_a, ((group_b_length * n_cycles) // group_a_length) + 1
        )[: group_b_length * n_cycles]


def generate_support_pairs(group_1: list, group_2: list, n_cycles: int) -> list:
    """Generates a list of 2-tuples containing a leading and assisting pair to work
    support.
    """
    group_1_lead = generate_lead_list(group_1, n_cycles)
    group_1_assist = generate_assist_list(group_1, group_2, n_cycles)

    group_2_lead = generate_lead_list(group_2, n_cycles)
    group_2_assist = generate_assist_list(group_2, group_1, n_cycles)

    support_pairs = []
    group_1_lead_index = 0
    group_2_lead_index = 0

    for i in range(n_cycles):
        for j in range(len(group_1)):
            support_pairs.append(
                (group_1_lead[group_1_lead_index], group_2_assist[group_1_lead_index])
            )
            group_1_lead_index += 1

        for k in range(len(group_2)):
            support_pairs.append(
                (group_2_lead[group_2_lead_index], group_1_assist[group_2_lead_index])
            )
            group_2_lead_index += 1

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


def main():
    service = create_service(
        google_calendar_api["client_secret_file"],
        google_calendar_api["api_name"],
        google_calendar_api["api_version"],
        google_calendar_api["scopes"],
    )
    calendar_id = google_calendar_api["calendar_ids"][google_calendar_api["calendar"]]

    g_sevens = support_team["g_sevens"]
    everyone_else = support_team["everyone_else"]

    start_date = string_to_datetime(date_range["start_date"])
    n_cycles = date_range["n_cycles"]
    n_days = n_cycles * (len(g_sevens) + len(everyone_else))
    workday_dates = get_workday_dates(start_date, n_days)

    if support_team["start_cycle_with"] == "g_sevens":
        support_pairs = generate_support_pairs(
            group_1=g_sevens, group_2=everyone_else, n_cycles=n_cycles
        )
    else:
        support_pairs = generate_support_pairs(
            group_1=everyone_else, group_2=g_sevens, n_cycles=n_cycles
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
        event_body["end"] = {"date": str(workday_dates[i] + timedelta(1))}

        write_calendar_event(service, calendar_id, event_body)

    everyone = list(g_sevens)
    everyone.extend(everyone_else)

    print(f"\nIn {n_days} working days:")
    for individual in everyone:
        lead_count = 0
        assist_count = 0

        for pair in support_pairs:
            if individual == pair[0]:
                lead_count += 1
            if individual == pair[1]:
                assist_count += 1

        print(
            f"{individual} has been scheduled to lead {lead_count} times and assist "
            f"{assist_count} times."
        )


if __name__ == "__main__":
    if support_team["start_cycle_with"] not in ["g_sevens", "everyone_else"]:
        raise ValueError(
            f"{support_team['start_cycle_with']} is an invalid group name."
        )
    main()
