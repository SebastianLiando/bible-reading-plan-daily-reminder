
import csv
from io import StringIO
from datetime import datetime
from bible.plan_manager import ReadingTask
from schedule.schedule_parser import ScheduleParser
from bible.bible import Bible
import pytest

test_csv = '''Dates,Week,Day 1,Day 2,Day 3,Day 4,Day 5,Day 6,Day 7,Remarks
03/01 - 09/01,1,,,,,,,,Preparation Phase
10/01 - 16/01,2,Matt 1,,2,,3,,4,
17/01 - 23/01,3,,5,,6,,7,,
24/01 - 30/01,4,8,,Luke 1,,10,,11,'''
content_stream = StringIO(test_csv)
reader = csv.reader(content_stream)
csv_data = list(reader)

start = datetime(2022, 1, 3)
bible = Bible()


def test_start_date():
    start_date = datetime(2021, 3, 15)
    parser = ScheduleParser(csv_data, start_date, bible)

    tasks = parser.get_tasks(start_date)
    assert tasks[0].date >= start_date.date()


def test_validate_headers_if_wrong_raises_exception():
    with pytest.raises(ValueError):
        ScheduleParser(csv_data, start, bible, ['Dates, Week'])


def test_parsing_is_correct():
    parser = ScheduleParser(csv_data, start, bible)
    target_date = datetime(2022, 1, 26)

    task = parser.get_tasks(target_date, target_date)[0]
    assert str(task) == str(ReadingTask('luke', 1, 1, 1000, target_date.date()))


def test_get_tasks_without_end_date():
    parser = ScheduleParser(csv_data, start, bible)

    from_date = datetime(2022, 1, 26)
    tasks = parser.get_tasks(from_date)
    for task in tasks:
        assert task.date >= from_date.date()


def test_get_tasks_with_end_date():
    parser = ScheduleParser(csv_data, start, bible)

    from_date = datetime(2022, 1, 15)
    to_date = datetime(2022, 1, 20)
    tasks = parser.get_tasks(from_date, to_date)

    for task in tasks:
        assert task.date >= from_date.date() and task.date <= to_date.date()
