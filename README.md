# Data engineering support rota
This repo contains a script that populates a Google Calendar with a support rota for the Data Engineering team.

## Usage
To work with this repo, first setup Python (this module has been tested with 3.8. The use of a virtual envionment of some sort is also recommended) and git-crypt. You'll ned to add your GPG key to the repo to decrypt it, details about how to do so can be found [here](.git-crypt/README.md).

WARNING :warning: Don't use this script on a calendar that is used for anything other than a support rota. The script will delete any events in the calendar before creating new ones, so you don't have to worry about creating duplicate events. :warning: WARNING

- Start by updating `settings.py` where you'll find three dictionaries:
    - Google Calendar API connection settings.
    - Adjust the start and end dates as necessary.
    - The support team is defined as those that are and aren't G7's.

- Log into the Google Calendar with the credentials provided in `google_calendar_login.txt`. These creds are for a dev calendar with the Google Calendar API enabled. You can use the `generate_rota.py` script to add events to any Google Calendar, but you will need to make sure API access is enabled.
- Run `pip install -r requirements.txt` (from within your virtual environment).
- Run `generate_rota.py`.
    - A browser window will open and you'll have to accept the access request.
    - A session token gets created so you don't have to do this every time.
    - If the rest of the script doesn't run immediately after accepting the access request, re-run it.
    - If the session token has expired, it gets deleted when you run the script. Run it again at this point.

- See the [data engineering wiki](https://github.com/moj-analytical-services/data-engineering/wiki/Data-Engineering-Support-Rota) for more details about support.

## Githooks
This repo comes with some githooks to make standard checks before you commit files to Github. The checks are: 
- if you're using git-crypt, run `git-crypt status` and check for unencrypted file warnings 
- run Black on Python files
- run Flake8 on Python files
- run yamllint on yaml files

If you want to use these, run this command from the repo's root directory: 

`git config core.hooksPath githooks`

By default hooks live in a .git subfolder that isn't version controlled. This repo instead keeps them in a folder called `githooks`, in a bash script called `pre-commit`. The command above tells your copy of the repo to look in this folder instead of the usual location. 

You can add these hooks to other repos by copying from this repo's githooks folder and pasting into the other repo's .git/hooks folder.

### Skipping the hooks
Once installed, the hooks run each time you commit. To skip them, add `--no-verify` to the end of your commit command. For exmaple, `git commit -m "Committing stuff" --no-verify`.

### Using Poetry
These hooks aren't set up to work with Poetry. They expect you to have Black, Flake8 and yamllint installed in the same environment you're in when you commit. 

This might change in the future.

## Formatting and linting configs
Config changes for flake8 go in .flake8. Our standard settings include:
- max line length to 88 to match team's preference (and Black default)
- ignore rule E203 which doesn't quite match PEP8 on spacing around colons (and conflicts with Black)
- ignore some folders like venv and .github

Config changes for yamllint should go in `.yamllint`. 

We use the standard Black config, so this repo doesn't include a config. To make config changes, add them to a file called `pyproject.toml`, under a line saying `[tool.black]`. 

## Licence
[MIT Licence](LICENCE.md)
