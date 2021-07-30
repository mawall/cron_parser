from sys import argv, stderr
from crontask import CronTask


if __name__ == '__main__':
    try:
        cron_task = CronTask(argv[1])
        cron_task.describe()
    except IndexError as e:
        print('Error: No cron string passed', file=stderr)
