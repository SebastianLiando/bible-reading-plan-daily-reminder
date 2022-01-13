from ast import parse
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

JCC_ORG_ID = 'jcc-english-30621951616'

UPCOMING_SECT_SELECTOR = 'div [data-testid="organizer-profile__future-events"]'
EVENT_ITEM_SELECTOR = 'div.eds-event-card-content__primary-content'

ANCHOR_SELECTOR = 'a'
CONTENT_SUB_SELECTOR = 'div.eds-event-card-content__sub-title'
FORMATTED_NAME_SELECTOR = 'div.eds-is-hidden-accessible'

DATETIME_FORMAT = "%a, %b %d, %H:%M"


@dataclass(eq=True, frozen=True)
class EventbriteEvent:
    name: str
    '''Name of the event.'''

    url: str
    '''URL of the event registration page.'''

    date_time: datetime
    '''When the event takes place.'''

    @property
    def date_time_label(self) -> str:
        return datetime.strftime(self.date_time, DATETIME_FORMAT)


def _parse_event_time(event_time: str) -> datetime:
    parsed = datetime.strptime(event_time, DATETIME_FORMAT)

    # Determine the year
    now = datetime.now()

    # Check if the date and month is before or after today.
    # If it is today or after, then the event happens this year.
    if parsed.month > now.month or parsed.month == now.month and parsed.day >= now.day:
        parsed = parsed.replace(year=now.year)
    else:
        parsed = parsed.replace(year=now.year + 1)

    return parsed


def _parse_event(primary_div: Tag) -> EventbriteEvent:
    anchor = primary_div.select_one(ANCHOR_SELECTOR)
    formatted_name = anchor.select_one(FORMATTED_NAME_SELECTOR)
    sub_div = primary_div.select_one(CONTENT_SUB_SELECTOR)

    return EventbriteEvent(
        name=formatted_name.text,
        url=anchor.attrs['href'],
        date_time=_parse_event_time(sub_div.text)
    )


def _get_upcoming_events(html: str) -> List[EventbriteEvent]:
    soup = BeautifulSoup(html, 'html.parser')
    upcoming_section = soup.select_one(UPCOMING_SECT_SELECTOR)
    upcoming_items = upcoming_section.select(EVENT_ITEM_SELECTOR)

    result = set()

    for event_div in upcoming_items:
        event = _parse_event(event_div)
        result.add(event)

    return list(result)


def _build_eventbrite_url(org_id: str) -> str:
    return f'https://www.eventbrite.sg/o/{org_id}'


def get_future_events(org_id: str) -> List[EventbriteEvent]:
    # Make network request to eventbrite
    url = _build_eventbrite_url(org_id)
    response = requests.get(url)
    response.raise_for_status()

    return _get_upcoming_events(response.text)


def get_event_on(date: datetime, org_id: str = JCC_ORG_ID) -> Optional[EventbriteEvent]:
    events = get_future_events(org_id)
    for event in events:
        if event.date_time.day == date.day and event.date_time.month == date.month:
            return event

    return None