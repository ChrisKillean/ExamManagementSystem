from datetime import timedelta
import datetime


def validate_deadlines(date_variable, previous_date_variable, academic_year, minimum_days):
    if date_variable is None:
        return 1
    elif date_variable < previous_date_variable + timedelta(days=minimum_days):
        return 2
    elif date_variable.year > academic_year.year + 1:
        return 3
    else:
        return 0


def validate_deadlines(date_variable, previous_date_variable, academic_year, minimum_days):
    if date_variable is None:
        return 1
    elif date_variable < previous_date_variable + timedelta(days=minimum_days):
        return 2
    else:
        latest_deadline = datetime.date(day=int(1), month=int(6), year=int(academic_year.year + 1))

        if date_variable > latest_deadline:
            return 3
        else:
            return 0
