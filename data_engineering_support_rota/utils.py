from datetime import datetime, timedelta
import random


def string_to_datetime(date: str) -> datetime:
    """Takes a date as a sting of the format YYYY-MM-DD and converts it to a datetime
    object.
    """
    return datetime.strptime(date, "%Y-%m-%d").date()


def get_workday_dates(start_date: datetime, n_days: int) -> list[datetime]:
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
