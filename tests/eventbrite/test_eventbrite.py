from datetime import datetime
from eventbrite import _next_sunday_of
import pytest


@pytest.mark.parametrize('start,next_sunday', [
    (datetime(2022, 1, 13), datetime(2022, 1, 16)),
    (datetime(2022, 1, 16), datetime(2022, 1, 23)),
])
def test_getting_next_sunday(start, next_sunday):
    assert _next_sunday_of(start).date() == next_sunday.date()
