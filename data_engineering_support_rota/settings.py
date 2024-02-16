google_calendar_api = {
    "client_secret_file": "data_engineering_support_rota_creds.json",
    "api_name": "calendar",
    "api_version": "v3",
    "scopes": ["https://www.googleapis.com/auth/calendar"],
    "calendar_ids": {
        "dev-1": "qk7dfadvnmao3lgvb207pqd1bk@group.calendar.google.com",
        "dev-2": (
            "3736415c8adfda50a2c3e0331dcd402321af0d48eee9f786d4458080d72111f7"
            "@group.calendar.google.com"
        ),
        "prod": "9c720gjf06r8odu2vhsfvd7e9k@group.calendar.google.com",
    },
    "calendar": "dev-1", # "dev-1" or "dev-2" for testing; "prod" for real
}

support_team = {
    "start_cycle_with": "g_sevens",
    "g_sevens": [
        "David",
        "Gustav",
        "Gwion",
        "Jacob",
        "Oliver",
        "Priya",
        "Soumaya",
        "Tapan",
        "Matt P"
    ],
    "everyone_else": [
        "Andy",
        "Ant",
        "Anthony",
        "Guy",
        "Matt H",
        "Matt L",
        "Murad",
        "Murdo",
        "Parminder",
        "Siva",
        "Theo",
        "Thomas",
        "Tom",
        "William"
    ],
}

date_range = {
    "start_date": "2024-02-07",
    "n_cycles": 4,
}
