# Data engineering support rota

This repo contains a script that populates a Google Calendar with a support rota for the data engineering team.

## Usage

To work with this repo, first setup Python (this repo has been tested with 3.8) and git-crypt (the use of a virtual envionment of some sort is also recommended). You'll need to add your GPG key to the repo to decrypt it, details about how to do so can be found [here](.git-crypt/README.md).

WARNING :warning: Don't use this script with a calendar that is used for anything other than the support rota. The script will delete any events from the given start date on, before creating new ones (this is so you don't have to worry about creating duplicate events). :warning: WARNING

- You'll need to update `settings.py` where there are three dictionaries containing:

  - Google Calendar API connection settings.
  - The start date and the number of cycles you want the calendar to run for.
    - One cycle is the number of days equal to the total number of people in the support team.
  - The support team, which is defined as those that are and aren't G7's.

- Log into the Google Calendar with the credentials provided in `google_calendar_login.txt`, these creds are for a dev calendar with the Google Calendar API enabled. You can use the `generate_rota.py` script to add events to any Google Calendar, but you will need to make sure API access is enabled.
- Run `pip install -r requirements.txt` (from within your virtual environment).
- Run `generate_rota.py`.

  - A browser window will open and you'll have to accept the access request.
    - A session token gets created so you don't have to do this every time.

- See the [data engineering wiki](https://github.com/moj-analytical-services/data-engineering/wiki/Data-Engineering-Support-Rota) for more details about support.

## Githooks

This repo comes with some githooks to make standard checks before you commit files to Github. The checks are:

- if you're using git-crypt, run `git-crypt status` and check for unencrypted file warnings
- run Black on Python files
- run Flake8 on Python files
- run yamllint on yaml files

### Skipping the hooks

Once installed, the hooks run each time you commit. To skip them, add `--no-verify` to the end of your commit command. For exmaple, `git commit -m "Committing stuff" --no-verify`.

## Formatting and linting configs

Config changes for flake8 go in .flake8. Our standard settings include:

- max line length to 88 to match team's preference (and Black default)
- ignore rule E203 which doesn't quite match PEP8 on spacing around colons (and conflicts with Black)
- ignore some folders like venv and .github

Config changes for yamllint should go in `.yamllint`.

We use the standard Black config, so this repo doesn't include a config. To make config changes, add them to a file called `pyproject.toml`, under a line saying `[tool.black]`.

## Licence

[MIT Licence](LICENCE.md)
