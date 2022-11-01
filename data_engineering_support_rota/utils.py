import calendar
from collections import Counter
from datetime import datetime, timedelta, date
import random


def string_to_datetime(date: str) -> date:
    """Takes a date as a sting of the format YYYY-MM-DD and converts it to a datetime
    object.
    """
    return datetime.strptime(date, "%Y-%m-%d").date()


def get_workday_dates(start_date: date, n_days: int) -> list[datetime]:
    """Generates a list of dates excluding weekends that is n_days long starting at
    start_date.
    """
    dates = []
    days_delta = 0

    while len(dates) != n_days:
        date = start_date + timedelta(days_delta)
        days_delta += 1
        if date.weekday() not in [5, 6]:
            dates.append(date)

    return dates


def repeat_and_shuffle_without_consecutive_elements(
    input_list: list, n_repeats: int
) -> list:
    """Repeats a list the specified number of times and shuffles it's elements whilst
    ensuring no two consecutive values are equal.
    Parameters
    ----------
    input_list : list
        The list you want to repeat and shuffle.
    n_repeats : int
        The number of times you want to repeat the input list.
    Returns
    -------
    list
        A list of length n_repeats * len(input_list), shuffled with no two consecutive
        values being equal.
    Raises
    ------
    ValueError
        If the input list contains duplicate values.
    """
    if len(set(input_list)) != len(input_list):
        raise ValueError("Remove the duplicate value in this list: ", input_list)

    output = list(input_list)
    random.shuffle(output)

    for _ in range(n_repeats - 1):
        shuffle_list = [element for element in input_list if element not in output[-1]]
        random.shuffle(shuffle_list)
        shuffle_list.append(output[-1])
        shuffle_list[1:] = random.sample(shuffle_list[1:], len(shuffle_list) - 1)
        output.extend(shuffle_list)

    return output


def generate_report(
    g_sevens: list[str],
    everyone_else: list[str],
    lead_workdays: list[tuple],
    assist_workdays: list[tuple],
    workday_dates: list[datetime],
    n_cyles: int,
    n_days: int,
    google_calendar: str,
    google_calendar_id: str,
) -> tuple[dict, dict]:
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
        # The lead_workday_count loop is redundant because the number of days working
        # support as lead should always be the same as n_cyles. But, it's nice to check
        # that the code has worked correctly.
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
            "env": google_calendar,
            "id": google_calendar_id,
        },
    }

    return days_worked_report, config_report
