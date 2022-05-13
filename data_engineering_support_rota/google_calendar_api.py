import os
import time
from typing import Union

from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_core import retry
from googleapiclient.discovery import build, Resource
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


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
    time.sleep(0.25)
