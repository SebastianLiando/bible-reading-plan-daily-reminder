from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import re
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

FALLBACK_URL = 'https://tinyurl.com/jcceng'
JCC_ORG_ID = 'jcc-english-30621951616'

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


def _parse_event_json(json: dict) -> EventbriteEvent:
    name = json['name']['text']
    url = json['url']
    date_time = datetime.fromisoformat(json['start']['local'])

    return EventbriteEvent(name=name, url=url, date_time=date_time)


def _get_server_data(script_section: Tag) -> dict:
    """Parse the server data json from the script.

    Args:
        script_section (Tag): The `<script>` containing server data.

    Raises:
        ValueError: If there is no server data found.

    Returns:
        dict: The server data json object.
    """
    content = script_section.text.split(';')

    index = -1
    for i, c in enumerate(content):
        if 'SERVER_DATA' in c:
            index = i

    if index == -1:
        raise ValueError('Server data cannot be found!')

    server_data_line = content[index].strip()
    server_data_json = re.match(
        '^window.__SERVER_DATA__ = (.+)$', server_data_line).group(1)
    server_data_json = json.loads(server_data_json)

    return server_data_json


def _get_upcoming_events(html: str) -> List[EventbriteEvent]:
    soup = BeautifulSoup(html, 'html.parser')

    # Find server data in the source code.
    # This is found in window.__SERVER_DATA__ inside on of the <script>
    scripts = soup.select('script')
    server_data = None
    for script in scripts:
        if 'window.__SERVER_DATA__' in script.text:
            server_data = _get_server_data(script)

    if server_data is None:
        raise ValueError('Cannot find server data!')

    future_events = server_data['view_data']['events']['future_events']
    future_events = set(map(_parse_event_json, future_events))
    return list(future_events)


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
        if event.date_time.date() == date.date():
            return event

    return None


def _next_sunday_of(dt: datetime) -> datetime:
    """Get the next coming Sunday. If today is Sunday, get the next week's Sunday instead.

    Args:
        dt (datetime): The starting datetime.

    Returns:
        datetime: The datetime of the next coming Sunday.
    """
    result = datetime.fromtimestamp(dt.timestamp())  # Make a copy

    while result.isoweekday() != 7 or result.date() == dt.date():
        result = result + timedelta(days=1)

    return result


def get_next_jcc_service() -> EventbriteEvent:
    next_sunday = _next_sunday_of(datetime.now())

    event = get_event_on(next_sunday)
    return event
