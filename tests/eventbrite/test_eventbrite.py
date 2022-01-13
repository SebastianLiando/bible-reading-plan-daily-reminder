from datetime import datetime, timedelta
from eventbrite import DATETIME_FORMAT, _parse_event_time

def test_date_parsing_today_correctly_parse_year():
    now = datetime.now()
    date_string = datetime.strftime(now, DATETIME_FORMAT)

    assert _parse_event_time(date_string).year == now.year

def test_date_parsing_tomorrow_correctly_parse_year():
    tomorrow = datetime.now() + timedelta(days=1)
    date_string = datetime.strftime(tomorrow, DATETIME_FORMAT)

    assert _parse_event_time(date_string).year == tomorrow.year

def test_date_parsing_past_correctly_parse_year():
    yesterday = datetime.now() + timedelta(days=-1)
    date_string = datetime.strftime(yesterday, DATETIME_FORMAT)

    assert _parse_event_time(date_string).year == yesterday.year + 1