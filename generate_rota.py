import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


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
