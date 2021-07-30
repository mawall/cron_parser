# Cron Expression Parser

Simple cron expression parser.

Expects a single cron string in the following format:
```Bash
"<minute> <hour> <day-of-month> <month> <day-of-week> <command>"
```

* Doesn't support special strings, such as `@hourly` or `@yearly`.
* Doesn't support `L`, `W` and `#`.
* `*` and `?` are treated as synonyms.
* All fields are independent of each other. For example:
  * When both `day_of_month` and `day_of_week` are specified, neither will be 
    adjusted according to the values of the other.
  * `day_of_month` is not adjusted for the number of days of the specified 
    month(s), but always has a maximum of 31 days.

<br>

Run with:
```Bash
python parser.py "*/15 0 1,15 * 1-5 /usr/bin/find"
```

Run tests with `pytest` or `python -m pytest`

<br>

Sample output:
```
$ python parser.py '*/15 0 1,15 * 1-5 /usr/bin/find'
minute        0 15 30 45
hour          0
day of month  1 15
month         1 2 3 4 5 6 7 8 9 10 11 12
day of week   1 2 3 4 5
command       /usr/bin/find
```