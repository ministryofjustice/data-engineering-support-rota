from datetime import datetime

start_date_string = "2000-01-01"
start_date = datetime.strptime(start_date_string, "%Y-%m-%d").date()
todays_date = datetime.today().date()
date_delta = (todays_date - start_date).days

print(date_delta)
