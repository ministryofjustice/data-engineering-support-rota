import calendar
from collections import Counter
from datetime import datetime, timedelta
import json
from math import ceil
import random

from google_calendar_api import (
    create_service,
    get_list_events_response,
    delete_calendar_event,
    write_calendar_event,
)
from settings import google_calendar_api, date_range, support_team
from utils import (
    string_to_datetime,
    get_workday_dates,
    repeat_and_shuffle_without_consecutive_elements,
)


def generate_lead_list(group: list[str], n_cycles: int) -> list:
    """A helper function that repeats the list, group, for n_cycles and shuffles each
    repitition.
    """
    random.shuffle(group)
    repeat_and_shuffle = []

    for _ in range(n_cycles):
        repeat_and_shuffle.extend(group)

    return repeat_and_shuffle


def generate_assist_list(group_a: list[str], group_b: list[str], n_cycles: int) -> list:
    """A helper function that takes group_a and repeats it the number of times required
    such that it's length is at least as long as the length of group_b * n_cycles. Each
    repitition is shuffled whilst ensuring no two consequtive elements are the same.
    Finally the repeated and shuffled group_a list is sliced to the exact length of
    group_b * n_cycles.
    """
    group_a_length = len(group_a)
    group_b_length = len(group_b)

    if group_a_length == group_b_length:
        return repeat_and_shuffle_without_consecutive_elements(group_a, n_cycles)

    else:
        return repeat_and_shuffle_without_consecutive_elements(
            group_a, ceil((group_b_length * n_cycles) / group_a_length)
        )[: group_b_length * n_cycles]


def generate_support_pairs(
    group_1: list[str],
    group_2: list[str],
    n_cycles: int,
    # n_days: int,
) -> list[tuple]:
    """Generates a list of 2-tuples containing a leading and assisting pair to work
    support.
    """
    group_1_length = len(group_1)
    group_2_length = len(group_2)
    support_pairs = []

    for _ in range(n_cycles):
        if group_1_length == group_2_length:
            group_a = list(group_1)
            random.shuffle(group_a)

            group_b = list(group_2)
            random.shuffle(group_b)

            support_pairs.extend(
                (leading, assisting) for leading, assisting in zip(group_a, group_b)
            )
            support_pairs.extend(
                (leading, assisting) for leading, assisting in zip(group_b, group_a)
            )
        elif group_1_length > group_2_length:
            group_a = list(group_1)
            random.shuffle(group_a)

            group_b = list(group_2)
            group_b = repeat_and_shuffle_without_consecutive_elements(
                group_2, ceil(group_1_length / group_2_length)
            )

            support_pairs.extend(
                (leading, assisting) for leading, assisting in zip(group_a, group_b)
            )

            group_a = list(group_1)
            random.shuffle(group_a)
            if support_pairs[-1][0] == group_a[0] or support_pairs[-1][1] == group_a[0]:
                group_a.append(group_a.pop(0))

            group_b = list(group_2)
            random.shuffle(group_b)
            while True:
                if (
                    support_pairs[-1][0] == group_b[0]
                    or support_pairs[-1][1] == group_b[0]
                ):
                    group_b.append(group_b.pop(0))
                else:
                    break

            support_pairs.extend(
                (leading, assisting) for leading, assisting in zip(group_b, group_a)
            )

        else:
            group_a = list(group_1)
            random.shuffle(group_a)
            print("len(group_a) lead:", len(group_a))
            group_b = list(group_2)
            random.shuffle(group_b)
            print("len(group_b) assist", len(group_b))
            support_pairs.extend(
                (leading, assisting) for leading, assisting in zip(group_a, group_b)
            )

            group_a = repeat_and_shuffle_without_consecutive_elements(
                group_1, ceil(group_2_length / group_1_length)
            )
            while True:
                if (
                    support_pairs[-1][0] == group_a[0]
                    or support_pairs[-1][1] == group_a[0]
                ):
                    group_a = repeat_and_shuffle_without_consecutive_elements(
                        group_1, ceil(group_2_length / group_1_length)
                    )
                else:
                    break
            print("len(group_a) assist:", len(group_a))
            group_b = list(group_2)
            random.shuffle(group_b)
            if support_pairs[-1][0] == group_b[0] or support_pairs[-1][1] == group_b[0]:
                group_b.append(group_b.pop(0))
            print("len(group_b) lead", len(group_b))
            support_pairs.extend(
                (leading, assisting) for leading, assisting in zip(group_b, group_a)
            )

    return support_pairs


# g_sevens = support_team["g_sevens"]
# everyone_else = support_team["everyone_else"]
# n_cycles = date_range["n_cycles"]

# if support_team["start_cycle_with"] == "g_sevens":
#     support_pairs = generate_support_pairs(
#         group_1=g_sevens, group_2=everyone_else, n_cycles=n_cycles
#     )
# else:
#     support_pairs = generate_support_pairs(
#         group_1=everyone_else, group_2=g_sevens, n_cycles=n_cycles
#     )

# print(support_pairs)


def get_report(
    g_sevens: list[str],
    everyone_else: list[str],
    lead_workdays: list[tuple],
    assist_workdays: list[tuple],
    workday_dates: list[datetime],
    n_cyles: int,
    n_days: int,
):
    lead_workday_counts = Counter(lead_workdays)
    assist_workday_counts = Counter(assist_workdays)

    days_worked_report = {}
    everyone = list(g_sevens)
    everyone.extend(everyone_else)
    for name in everyone:
        days_worked_report[name] = {"lead_workdays": [], "assist_workdays": []}

    for lead_individual in lead_workday_counts.items():
        lead_name = lead_individual[0][0]
        lead_workday = calendar.day_name[lead_individual[0][1]]
        lead_workday_count = lead_individual[1]

        days_worked_report[lead_name]["lead_workdays"].append(
            (lead_workday, lead_workday_count)
        )

    for assist_individual in assist_workday_counts.items():
        assist_name = assist_individual[0][0]
        assist_workday = calendar.day_name[assist_individual[0][1]]
        assist_workday_count = assist_individual[1]

        days_worked_report[assist_name]["assist_workdays"].append(
            (assist_workday, assist_workday_count)
        )

    for individual in days_worked_report.items():
        # The following loop is redundant because the number of days working support as
        # lead should always be the same as n_cyles. But, it's nice to check that the
        # code has worked correctly.
        lead_count = 0
        for lead_workday_count in individual[1]["lead_workdays"]:
            lead_count += lead_workday_count[1]

        assist_count = 0
        for assist_workday_count in individual[1]["assist_workdays"]:
            assist_count += assist_workday_count[1]

        days_worked_report[individual[0]]["totals"] = (
            ("lead_days", lead_count),
            ("assist_days", assist_count),
            ("grand_total", lead_count + assist_count),
        )

    config_report = {
        "date_range": {
            "start": str(workday_dates[0]),
            "end": str(workday_dates[-1]),
            "n_cyles": n_cyles,
            "total_days": n_days,
        },
        "calendar": {
            "env": google_calendar_api["calendar"],
            "id": google_calendar_api["calendar_ids"][google_calendar_api["calendar"]],
        },
    }

    return days_worked_report, config_report


def main():
    if support_team["start_cycle_with"] not in ["g_sevens", "everyone_else"]:
        raise ValueError(
            f"{support_team['start_cycle_with']} is an invalid group name."
        )

    # service = create_service(
    #     google_calendar_api["client_secret_file"],
    #     google_calendar_api["api_name"],
    #     google_calendar_api["api_version"],
    #     google_calendar_api["scopes"],
    # )
    # calendar_id = google_calendar_api["calendar_ids"][google_calendar_api["calendar"]]

    g_sevens = support_team["g_sevens"]
    everyone_else = support_team["everyone_else"]

    start_date = string_to_datetime(date_range["start_date"])
    n_cycles = date_range["n_cycles"]
    n_days = n_cycles * (len(g_sevens) + len(everyone_else))
    workday_dates = get_workday_dates(start_date, n_days)

    if support_team["start_cycle_with"] == "g_sevens":
        support_pairs = generate_support_pairs(
            group_1=g_sevens, group_2=everyone_else, n_cycles=n_cycles
        )
    else:
        support_pairs = generate_support_pairs(
            group_1=everyone_else, group_2=g_sevens, n_cycles=n_cycles
        )
    print("len(support_pairs)", len(support_pairs))
    print("n_days", n_days)
    # print(f"Deleting all calendar events from {date_range['start_date']} onwards...")
    # page_token = None
    # while True:
    #     response = get_list_events_response(
    #         service, calendar_id, page_token, date_range["start_date"]
    #     )
    #     events = response.get("items", [])

    #     for event in events:
    #         delete_calendar_event(service, calendar_id, event["id"])
    #     page_token = response.get("nextPageToken", None)

    #     if not page_token:
    #         break

    lead_workdays = []
    assist_workdays = []
    event_body = {}
    # print("Writing rota to calendar...")
    for i in range(n_days):
        event_body["summary"] = (
            f"{support_pairs[i][0]} is on support today with {support_pairs[i][1]} "
            "assisting"
        )
        event_body["start"] = {"date": str(workday_dates[i])}
        event_body["end"] = {"date": str(workday_dates[i] + timedelta(1))}

        # write_calendar_event(service, calendar_id, event_body)

        lead_workdays.append((support_pairs[i][0], workday_dates[i].weekday()))
        assist_workdays.append((support_pairs[i][1], workday_dates[i].weekday()))

    days_worked_report, config_report = get_report(
        g_sevens,
        everyone_else,
        lead_workdays,
        assist_workdays,
        workday_dates,
        n_cycles,
        n_days,
    )

    with open("../docs/days_worked_report.json", "w") as file:
        json.dump(days_worked_report, file)
    with open("../docs/config_report.json", "w") as file:
        json.dump(config_report, file)

    print(f"\nIn {n_days} working days:")
    for individual in days_worked_report.items():
        name = individual[0]
        lead_count = individual[1]["totals"][0][1]
        assist_count = individual[1]["totals"][1][1]
        print(
            f"{name} has been scheduled to lead support {lead_count} times and assist "
            f"{assist_count} times."
        )


if __name__ == "__main__":
    main()
