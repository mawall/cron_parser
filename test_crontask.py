import pytest

from crontask import CronTask


class TestCronTask:
    @pytest.mark.parametrize("field, expected", [
        ("minute",          [i for i in range(0, 60)]),
        ("hour",            [i for i in range(0, 24)]),
        ("day_of_month",    [i for i in range(1, 32)]),
        ("month",           [i for i in range(1, 13)]),
        ("day_of_week",     [i for i in range(1, 8)]),
    ])
    def test_wildcard(self, field, expected):
        cron_str = '* * * * * cmd'
        cron_task = CronTask(cron_str)
        assert getattr(cron_task, field) == expected

    @pytest.mark.parametrize("field, expected", [
        ("minute",          [15]),
        ("hour",            [15]),
        ("day_of_month",    [1]),
        ("month",           [6]),
        ("day_of_week",     [1]),
    ])
    def test_single_value(self, field, expected):
        cron_str = '15 15 1 6 1 cmd'
        cron_task = CronTask(cron_str)
        assert getattr(cron_task, field) == expected

    @pytest.mark.parametrize("field, expected", [
        ("minute",          [15, 30, 45]),
        ("hour",            [0, 12, 18]),
        ("day_of_month",    [1, 2, 3]),
        ("month",           [6, 12]),
        ("day_of_week",     [1, 2, 3, 4, 5]),
    ])
    def test_list(self, field, expected):
        cron_str = '15,30,45 0,12,18 1,2,3 6,12 1,2,3,4,5 cmd'
        cron_task = CronTask(cron_str)
        assert getattr(cron_task, field) == expected

        cron_str = '15,30,45 0,12,18 1,2,3 JUN,DEC MON,TUE,WED,THU,FRI cmd'
        cron_task = CronTask(cron_str)
        assert getattr(cron_task, field) == expected

    @pytest.mark.parametrize("field, expected", [
        ("minute",          [i for i in range(15, 31)]),
        ("hour",            [i for i in range(2, 4)]),
        ("day_of_month",    [i for i in range(1, 6)]),
        ("month",           [i for i in range(1, 3)]),
        ("day_of_week",     [i for i in range(1, 6)]),
    ])
    def test_range(self, field, expected):
        cron_str = '15-30 2-3 1-5 1-2 1-5 cmd'
        cron_task = CronTask(cron_str)
        assert getattr(cron_task, field) == expected

        cron_str = '15-30 2-3 1-5 JAN-FEB MON-FRI cmd'
        cron_task = CronTask(cron_str)
        assert getattr(cron_task, field) == expected

    @pytest.mark.parametrize("field, expected", [
        ("minute",          [i for i in range(0, 60, 5)]),
        ("hour",            [i for i in range(0, 24, 2)]),
        ("day_of_month",    [i for i in range(1, 32, 2)]),
        ("month",           [i for i in range(1, 13, 6)]),
        ("day_of_week",     [i for i in range(1, 8, 3)]),
    ])
    def test_increment_from_star(self, field, expected):
        cron_str = '*/5 */2 */2 */6 */3 cmd'
        cron_task = CronTask(cron_str)
        assert getattr(cron_task, field) == expected

    @pytest.mark.parametrize("field, expected", [
        ("minute",          [i for i in range(15, 60, 5)]),
        ("hour",            [i for i in range(12, 24, 2)]),
        ("day_of_month",    [i for i in range(10, 32, 2)]),
        ("month",           [i for i in range(6, 13, 2)]),
        ("day_of_week",     [i for i in range(3, 8, 2)]),
    ])
    def test_increment_from_value(self, field, expected):
        cron_str = '15/5 12/2 10/2 6/2 3/2 cmd'
        cron_task = CronTask(cron_str)
        assert getattr(cron_task, field) == expected

        cron_str = '15/5 12/2 10/2 JUN/2 WED/2 cmd'
        cron_task = CronTask(cron_str)
        assert getattr(cron_task, field) == expected

