import json
import os

import requests
from requests.exceptions import HTTPError, RequestException, URLRequired
from datetime import datetime, date

# Get hook from GitHub secrets
hook = os.getenv("TEST_GCAL_HOOK")
# hook = os.getenv("DATA_ENG_HOOK")

base_url = "https://hooks.slack.com/services/"


# Get today's event details from calendar
today = date.today()
time = datetime.time()

# Send message to slack channel
def send_message(content, webhook):  # send message to webhook
    message = {"text": content}
    message_json = json.dumps(message)
    return requests.post(webhook, message_json)

text = f"Today's date is {today}, and the time is {time}"
webhook_endpoint = f"{base_url}{hook}"

send_message(text, webhook_endpoint)  

# python .github/scripts/notify-channel.py

# 1. connect to calendar and get calendar event details
# 2. use webhook from github secrets to schedule messages

