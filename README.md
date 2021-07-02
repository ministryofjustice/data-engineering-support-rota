# Data engineering support rota

This repo contains a script that populates a Google Calendar with a support rota for the data engineering team.

## Usage

To work with this repo, first setup Python (this repo has been tested with 3.8) and git-crypt (the use of a virtual envionment of some sort is also recommended). You'll need to add your GPG key to the repo to decrypt it, details about how to do so can be found [here](.git-crypt/README.md).

WARNING :warning: Don't use this script with a calendar that is used for anything other than the support rota. The script will delete any events from the specified start date onwards, before creating new ones (this is so you don't have to worry about creating duplicate events). :warning: WARNING

- You'll need to update `settings.py` where there are three dictionaries containing:

  - Google Calendar API connection settings.
    - There are two default calendar IDs, `dev` and `prod`, update the `calendar` value to one of these.
  - The start date and the number of cycles you want the calendar to run for.
    - It's not compulsory but if updating an existing calendar, you should set the start date to begin when the cycle switches from G7s to everyone else, or vice versa.
    - One cycle is the number of days equal to the total number of individuals in the support team.
  - The support team is made up of two groups, which is defined as those that are G7s and aren't.
    - Update the team if needed and select which group to start a cycle with.

- Log into the Google Calendar with the credentials provided in `google_calendar_login.txt`, these creds are for a dev calendar with the Google Calendar API enabled. You can use the `generate_rota.py` script to add events to any Google Calendar, but you will need to make sure API access is enabled and you've added the appropriate calendar ID to `settings.py`.
- Run `pip install -r requirements.txt` (from within your virtual environment).
- Run `generate_rota.py`.

  - A browser window will open and you'll have to accept the access request.
    - A session token gets created so you don't have to do this every time.

- See the [data engineering wiki](https://github.com/moj-analytical-services/data-engineering/wiki/Data-Engineering-Support-Rota) for more details about support.

## Licence

[MIT Licence](LICENCE.md)
