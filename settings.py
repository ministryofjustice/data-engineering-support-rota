google_calendar_api = {
    "client_secret_file": "data_engineering_support_rota_creds.json",
    "api_name": "calendar",
    "api_version": "v3",
    "scopes": ["https://www.googleapis.com/auth/calendar"],
    "calendar_id": {
        "dev": "qk7dfadvnmao3lgvb207pqd1bk@group.calendar.google.com",
        "prod": "9c720gjf06r8odu2vhsfvd7e9k@group.calendar.google.com",
    },
}

support_team = {
    "start_cycle_with": "g_sevens",
    "g_sevens": [
        "George",
        "Calum",
        "Karik",
        "Jacob",
        "Kimberley",
    ],
    "everyone_else": [
        "Thomas",
        "Jake",
        "Tapan",
        "Darius",
        "Anthony",
        "David",
        "Danjiv",
        "Lora",
        "Stephen",
    ],
}

date_range = {
    "start_date": "2021-07-14",
    "n_cycles": 10,
}
