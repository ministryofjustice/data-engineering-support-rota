import json
import os
import sys
import getopt

import requests
from requests.exceptions import HTTPError, RequestException, URLRequired
from datetime import date

# POST https://hooks.slack.com/services/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
# Content-type: application/json
# {
#     "text": "Hello, world."
# }

base_url = "https://hooks.slack.com/services/"
hook  = "T02DYEB3A/B04S06LHW3V/JHNvwWGShEoFFABQr9lZDMqA"
#test = "hello world!"

#requests.post(f"{base_url}{hook}", data=test)

# This works run from terminal
#curl -X POST -H 'Content-type: application/json' --data '{"text": "Hello, world."}' https://hooks.slack.com/services/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

# need functions to get the message and send it
# daily workflow to collect the message for the day from the calendar

today = date.today()

def send_message(content, webhook):  # send message to webhook
    message = {"text": content}
    message_json = json.dumps(message)
    return requests.post(webhook, message_json)

text = f"Today's date is {today}"
webhook_endpoint = f"{base_url}{hook}"

send_message(text, webhook_endpoint)  