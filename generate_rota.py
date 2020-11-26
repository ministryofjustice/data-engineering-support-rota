# support list is a csv in repo

# check day
# if greater than monday set rota start date to next monday

# iterate through list of support
# assign to date

import copy
import datetime

support = {
    0: ("George", "Alec"),
    1: ("Adam", "Darius"),
    2: ("Calum", "Thomas"),
    3: ("Karik", "Jake"),
    4: ("Sam", "Tapan"),
    5: ("Jacob", "Anthony"),
    6: ("Kimberley", "David"),
    7: ("Alec", "George"),
    8: ("Darius", "Adam"),
    9: ("Thomas", "Calum"),
    10: ("Jake", "Karik"),
    11: ("Tapan", "Sam"),
    12: ("Anthony", "Jacob"),
    13: ("David", "Kimberley"),
}


calendar = {
  "kind": "calendar#event",
  "etag": etag,
  "id": string,
  "status": string,
  "htmlLink": string,
  "created": datetime,
  "updated": datetime,
  "summary": string,
  "description": string,
  "location": string,
  "colorId": string,
  "creator": {
    "id": string,
    "email": string,
    "displayName": string,
    "self": boolean
  },
  "organizer": {
    "id": string,
    "email": string,
    "displayName": string,
    "self": boolean
  },
  "start": {
    "date": date,
    "dateTime": datetime,
    "timeZone": string
  },
  "end": {
    "date": date,
    "dateTime": datetime,
    "timeZone": string
  },
  "endTimeUnspecified": boolean,
  "recurrence": [
    string
  ],
  "recurringEventId": string,
  "originalStartTime": {
    "date": date,
    "dateTime": datetime,
    "timeZone": string
  },
  "transparency": string,
  "visibility": string,
  "iCalUID": string,
  "sequence": integer,
  "attendees": [
    {
      "id": string,
      "email": string,
      "displayName": string,
      "organizer": boolean,
      "self": boolean,
      "resource": boolean,
      "optional": boolean,
      "responseStatus": string,
      "comment": string,
      "additionalGuests": integer
    }
  ],
  "attendeesOmitted": boolean,
  "extendedProperties": {
    "private": {
      (key): string
    },
    "shared": {
      (key): string
    }
  },
  "hangoutLink": string,
  "conferenceData": {
    "createRequest": {
      "requestId": string,
      "conferenceSolutionKey": {
        "type": string
      },
      "status": {
        "statusCode": string
      }
    },
    "entryPoints": [
      {
        "entryPointType": string,
        "uri": string,
        "label": string,
        "pin": string,
        "accessCode": string,
        "meetingCode": string,
        "passcode": string,
        "password": string
      }
    ],
    "conferenceSolution": {
      "key": {
        "type": string
      },
      "name": string,
      "iconUri": string
    },
    "conferenceId": string,
    "signature": string,
    "notes": string,
  },
  "gadget": {
    "type": string,
    "title": string,
    "link": string,
    "iconLink": string,
    "width": integer,
    "height": integer,
    "display": string,
    "preferences": {
      (key): string
    }
  },
  "anyoneCanAddSelf": boolean,
  "guestsCanInviteOthers": boolean,
  "guestsCanModify": boolean,
  "guestsCanSeeOtherGuests": boolean,
  "privateCopy": boolean,
  "locked": boolean,
  "reminders": {
    "useDefault": boolean,
    "overrides": [
      {
        "method": string,
        "minutes": integer
      }
    ]
  },
  "source": {
    "url": string,
    "title": string
  },
  "attachments": [
    {
      "fileUrl": string,
      "title": string,
      "mimeType": string,
      "iconLink": string,
      "fileId": string
    }
  ]
}


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
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)


todays_date = datetime.date.today()
the_weekday = todays_date.weekday()

# print("it's ", calendar.day_name[the_day], todays_date)
next_monday = next_weekday(todays_date, 0)  # 0=Mon, 1=Tue, 2=Wed...
this_weeks_rota = copy.deepcopy(calendar)
i = 4  # this will be written to a file at the end of the script and read in at the beginning to persit the index position of the support rota

for i in range(i, i + 5):
    this_weeks_rota["event"] = (
        f"{support[i][0]} is on support today with {support[i][1]} assisting."
    )
    this_weeks_rota["date"] = next_monday
    this_weeks_rota["all_day"] = "y"
    this_weeks_rota["time"] = None
    this_weeks_rota["duration"] = None

# does there need to be some logic to determine what date to start the week on based on if the script is running on monday or not?
print(this_weeks_rota)