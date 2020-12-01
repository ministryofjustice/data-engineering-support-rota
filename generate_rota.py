import copy
from datetime import datetime
from pathlib import Path

from apiclient.discovery import build
from google_auth_oauthlib.flow import Flow


start_date_string = "2000-01-01"
start_date = datetime.strptime(start_date_string, "%Y-%m-%d").date()
todays_date = datetime.today().date()
date_delta = todays_date - start_date

support = (
    ("George", "Alec"),
    ("Adam", "Darius"),
    ("Calum", "Thomas"),
    ("Karik", "Jake"),
    ("Sam", "Tapan"),
    ("Jacob", "Anthony"),
    ("Kimberley", "David"),
    ("Alec", "George"),
    ("Darius", "Adam"),
    ("Thomas", "Calum"),
    ("Jake", "Karik"),
    ("Tapan", "Sam"),
    ("Anthony", "Jacob"),
    ("David", "Kimberley"),
)

calendar = {}


def next_weekday(date, weekday: int):
    """Returns the next date of a given weekday.

    Parameters
    ----------
    date : datetime
        The date from which you want get the date of the next occurance of a particular day of the week.
    weekday : int
        The weekday you want the next occuring date for.

    Returns
    -------
    datetime
        The date of the next occurance of a particular day of the week from the given date.
    """
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0:  # if the target day has already happened this week
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)


this_weeks_rota = copy.deepcopy(calendar)
i = 4  # this will be written to a file at the end of the script and read in at the beginning to persit the index position of the support rota

for i in range(i, i + 5):
    this_weeks_rota[
        "event"
    ] = f"{support[i][0]} is on support today with {support[i][1]} assisting."
    this_weeks_rota["date"] = next_monday
    this_weeks_rota["all_day"] = "y"
    this_weeks_rota["time"] = None
    this_weeks_rota["duration"] = None

# add some logic to determine what date to start the week on based on if the script is running on monday or not?
print(this_weeks_rota)


flow = Flow.from_client_secrets_file(
    Path.cwd().parent / "data-engineering-support-rota.json",
    scopes=["https://www.googleapis.com/auth/calendar.events"],
    redirect_uri="urn:ietf:wg:oauth:2.0:oob",
)

auth_url, _ = flow.authorization_url(prompt="consent")

print("Please go to this URL: {}".format(auth_url))

code = input("Enter the authorization code: ")
flow.fetch_token(code=code)

session = flow.authorized_session()
print(session.get("https://www.googleapis.com/userinfo/v3/me").json())
