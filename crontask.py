from enum import IntEnum


class Month(IntEnum):
    JAN = 1
    FEB = 2
    MAR = 3
    APR = 4
    MAY = 5
    JUN = 6
    JUL = 7
    AUG = 8
    SEP = 9
    OCT = 10
    NOV = 11
    DEC = 12

    @classmethod
    def has(cls, val):
        return val.upper() in cls.__members__


class WeekDay(IntEnum):
    MON = 1
    TUE = 2
    WED = 3
    THU = 4
    FRI = 5
    SAT = 6
    SUN = 7

    @classmethod
    def has(cls, val):
        return val.upper() in cls.__members__


def parse_list(field, field_range, field_name):
    """Parses a cron field in list notation (1,2,3)."""
    min_lo, max_hi = field_range
    values = field.split(',')

    if all(v.isnumeric() and min_lo <= int(v) <= max_hi for v in values):
        f = int
    elif field_name == 'month' and all(Month.has(v) for v in values):
        f = lambda key: Month[key.upper()].value
    elif field_name == 'day_of_week' and all(WeekDay.has(v) for v in values):
        f = lambda key: WeekDay[key.upper()].value
    else:
        raise ValueError(f'malformatted cron field {field_name}: {field}')

    field_values = list(map(f, values))

    return field_values


def parse_range(field, field_range, field_name):
    """Parses a cron field in range notation (1-5)."""
    min_lo, max_hi = field_range
    values = field.split('-')

    if not len(values) == 2:
        raise ValueError(f'malformatted cron field {field_name}: {field}')

    lo, hi = values

    if all(v.isnumeric() and min_lo <= int(v) <= max_hi for v in values):
        lo, hi = int(lo), int(hi)
    elif field_name == 'month' and all(Month.has(v) for v in values):
        lo, hi = Month[lo.upper()].value, Month[hi.upper()].value
    elif field_name == 'day_of_week' and all(WeekDay.has(v) for v in values):
        lo, hi = WeekDay[lo.upper()].value, WeekDay[hi.upper()].value
    else:
        raise ValueError(f'malformatted cron field {field_name}: {field}')

    field_values = [i for i in range(lo, hi + 1)]

    return field_values


def parse_increments(field, field_range, field_name):
    """Parses a cron field in increment notation (*/5)."""
    min_lo, max_hi = field_range
    values = field.split('/')

    if not len(values) == 2:
        raise ValueError(f'malformatted cron field {field_name}: {field}')

    start, increment = values

    if start == '*':
        start = min_lo
    elif start.isnumeric() and min_lo <= int(start) <= max_hi:
        start = int(start)
    elif field_name == 'month' and Month.has(start):
        start = Month[start.upper()].value
    elif field_name == 'day_of_week' and WeekDay.has(start):
        start = WeekDay[start.upper()].value
    else:
        raise ValueError(f'malformatted cron field {field_name}: {field}')

    if not increment.isnumeric():
        raise ValueError(f'malformatted cron field {field_name}: {field}')

    field_values = [i for i in range(start, max_hi + 1, int(increment))]

    return field_values


def parse_cron_field(field, field_range, field_name):
    """Parses a single cron field and returns all values for it.

    Args:
        field: A string representing the cron field, e.g. '*/5'.
        field_range: A tuple representing the lowest and highest possible value
            for the respective cron field.
        field_name: A string representing the name of the respective cron field.

    Returns:
        A list of integer values for the respective field.

    Raises:
        ValueError: A malformatted cron field has been passed.
    """
    if field.isnumeric():
        field_values = [int(field)]
    elif field_name == 'month' and Month.has(field):
        field_values = [Month[field.upper()].value]
    elif field_name == 'day_of_week' and WeekDay.has(field):
        field_values = [WeekDay[field.upper()].value]
    elif field in ('*', '?'):
        lo, hi = field_range
        field_values = [i for i in range(lo, hi + 1)]
    elif ',' in field:
        field_values = parse_list(field, field_range, field_name)
    elif '-' in field:
        field_values = parse_range(field, field_range, field_name)
    elif '/' in field:
        field_values = parse_increments(field, field_range, field_name)
    else:
        raise ValueError(f'malformatted cron field {field_name}: {field}')

    return field_values


def parse_cron_str(cron_str, cron_field_names, cron_field_ranges):
    """Parses the cron string and returns all values for each field.

    Args:
        cron_str: The cron string.
        cron_field_names: A list of strings with names of each cron field.
        cron_field_ranges: A list of tuples with allowed ranges per cron field.

    Returns:
        A list of lists of integer values for the respective field. Each row
        represents a cron field as a list of integer values, e.g. minutes of
        hours. For example:

        [[0, 15, 30, 45],
         [0],
         [1, 15],
         [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
         [1, 2, 3, 4, 5],
         '/usr/bin/find']
    """
    field_values = []
    cron_fields = cron_str.split(' ')

    for field, field_range, field_name in zip(cron_fields,
                                              cron_field_ranges,
                                              cron_field_names):
        field_values.append(parse_cron_field(field, field_range, field_name))

    cmd = cron_fields[-1]
    field_values.append(cmd)

    return field_values


def validate_cron_str(cron_str):
    """Verifies that the cron string is formatted correctly.

    Args:
        cron_str: The cron string.

    Raises:
        ValueError: A malformatted cron string has been passed.
    """
    if not isinstance(cron_str, str):
        raise ValueError('first argument must be a string')

    cron_fields = cron_str.split(' ')
    if len(cron_fields) < 6:
        raise ValueError('not enough cron fields')
    elif len(cron_fields) > 6:
        raise ValueError('too many cron fields')


class CronTask:
    """Wraps all information relating to a cron task.

    Attributes:
        cron_str: The cron string.
        minute: A list of integers representing minutes.
        hour: A list of integers representing hours.
        day_of_month: A list of integers representing days of the month.
        month: A list of integers representing months.
        day_of_week: A list of integers representing days of the week.
        command: A string representing the command to be run.
    """

    cron_field_names = [
        'minute',
        'hour',
        'day_of_month',
        'month',
        'day_of_week',
    ]

    cron_field_ranges = [
        (0, 59),
        (0, 23),
        (1, 31),
        (1, 12),
        (1, 7),
    ]

    def __init__(self, cron_str):
        self.cron_str = cron_str
        validate_cron_str(cron_str)
        (
            self.minute,
            self.hour,
            self.day_of_month,
            self.month,
            self.day_of_week,
            self.command
        ) = parse_cron_str(cron_str,
                           self.cron_field_names,
                           self.cron_field_ranges)

    def describe(self, col_width=14):
        description = ''

        for field_name in self.cron_field_names:
            field_values = " ".join(str(value) for value
                                    in getattr(self, field_name))
            field_name = field_name.replace('_', ' ')
            description += f'{field_name:{col_width}}{field_values}\n'

        description += f'{"command":{col_width}}{self.command}\n'
        print(description)
