from datetime import date, datetime

DATE_FORMAT = "%Y-%m-%d"


def parse_date(text):
    return datetime.strptime(str(text).strip(), DATE_FORMAT).date()


def is_valid_date(text):
    try:
        parse_date(text)
    except ValueError:
        return False
    return True


def days_left(deadline):
    return (parse_date(deadline) - date.today()).days


def describe_days(n):
    if n < 0:
        return f"OVERDUE by {-n} day(s)"
    if n == 0:
        return "due today"
    if n == 1:
        return "due tomorrow"
    return f"due in {n} days"


def format_minutes(minutes):
    hours, mins = divmod(int(minutes), 60)
    if hours and mins:
        return f"{hours}h {mins}m"
    if hours:
        return f"{hours}h"
    return f"{mins}m"
