import telegram
from bible.utils import get_superscript
from bot_token import TOKEN
from bible.bible import Bible
from data.subscriber_repository import SubscriberRepository
from data.plan_repository import PlanRepository
from bible.plan_manager import ReadingTask
from google.cloud import firestore
from typing import List, Optional, Set, Tuple
from time import strftime
from datetime import date, datetime
from bible.bible_gateway import BibleGateway, BibleGatewayParser


def get_date_today() -> date:
    """Return today's date. The timezone is based on the system region.

    Returns:
        date: The date of today.
    """
    return datetime.now().date()


def format_date_today(today: date) -> str:
    return strftime('%B %d, %Y', today.timetuple())


def get_reading_plan_day_number() -> int:
    today = get_date_today()
    start_date = datetime(2021, 1, 7).date()

    delta = today - start_date
    num_of_days_from_first_jan = delta.days + 1
    num_of_sundays = delta.days // 7

    return num_of_days_from_first_jan - num_of_sundays


def get_today_reading_plan(db: firestore.Client) -> Optional[ReadingTask]:
    """Returns the reading plan for today if any from firestore.

    Args:
        db (firestore.Client): The database client.

    Returns:
        Optional[ReadingTask]: The reading plan, or None if it does not exist.
    """
    # Get today's date
    today_date = get_date_today()

    # Query today's plan from the database
    plan_repo = PlanRepository(db)
    return plan_repo.get_plan_at(today_date)


def get_verses_from_reading_task(bible: Bible, task_today: ReadingTask) -> List[str]:
    """Returns the Bible verses from a `ReadingTask` object.

    Args:
        bible (Bible): The Bible.
        task_today (ReadingTask): The reading task for today.

    Returns:
        List[str]: The Bible verses.
    """
    return bible.get_verses_from_chapter(
        task_today.book,
        task_today.chapter,
        task_today.start_verse,
        task_today.end_verse
    )


def beautify_verses(verses: List[str], separator: str = '\n') -> str:
    """Formats the Bible verses. This adds the verse number before the verse, and then separate
    the verses using the separator.

    Args:
        verses (List[str]): The Bible verses.
        separator (str, optional): The separator between verses. Defaults to '\n'.

    Returns:
        str: The neatly formatted Bible verses.
    """
    result = ['' for _ in range(len(verses))]

    # Add the verse numbers to each verse.
    for i in range(0, len(verses)):
        verse_no = get_superscript(i + 1)

        result[i] = f"{verse_no} {verses[i]}"

    # Join to a single string
    return separator.join(result)


def format_footnotes(footnotes: List[Tuple[str, str]]) -> str:
    result = []

    for i in range(len(footnotes)):
        alphabet = chr(ord('a') + i)

        (verse, footnote) = footnotes[i]
        result.append(f'{alphabet}. {verse} - {footnote}')

    return '\n'.join(result)


def get_subscribers(db: firestore.Client) -> Set[str]:
    """Returns subscriber ids from firestore.

    Args:
        db (firestore.Client): The firestore client.

    Returns:
        Set[str]: Subscribers' telegram chat ids.
    """
    repo = SubscriberRepository(db)

    return repo.get_subscribers()


def get_verses_from_fallback(task: ReadingTask, bible: Bible) -> str:
    # Get verses for today.
    today_verses = get_verses_from_reading_task(bible, task)

    # Format the verses nicely
    return beautify_verses(today_verses)


def get_data_from_bible_gateway(task: ReadingTask, bible: Bible) -> Tuple[str, List[Tuple[str, str]]]:
    book = bible.fuzzy_search_book(task.book)
    chapter = task.chapter
    (start, end) = bible.get_verse_range(
        book, chapter,
        task.start_verse, task.end_verse
    )

    # Call bible gateway to get the html source
    gateway = BibleGateway()
    raw = gateway.get_html(book, chapter)

    parser = BibleGatewayParser(raw)

    # Get the verses
    verses = parser.extract_verses(from_verse=start, to_verse=end)

    # Get the footnotes
    footnotes = parser.get_footnotes()

    return (verses, footnotes)


def format_telegram_message(task: ReadingTask, verses: str, footnotes: List[Tuple[str, str]]) -> str:
    # Today's date, formatted
    today_date = f'📅 <b>{format_date_today(get_date_today())}</b>'

    # Reading plan, formatted
    reading_chapter = f'{task.book.upper()} {task.chapter}'
    reading_plan = f'📖 Bible Reading Day {get_reading_plan_day_number()} - <b>{reading_chapter}</b>'

    # The message lines to be sent.
    message_lines = [
        today_date,
        reading_plan,
        '\n',
        verses,
    ]

    # Add footnote if any
    if not footnotes is None and len(footnotes) > 0:
        formatted_footnotes = format_footnotes(footnotes)
        message_lines.append('\n')
        message_lines.append('📝 <b>Footnotes</b>')
        message_lines.append(formatted_footnotes)

    return '\n'.join(message_lines)


def main():
    # Create the database client
    db = firestore.Client()

    # Get today's reading plan.
    task_today = get_today_reading_plan(db)

    # If there is no plan for today, the task ends
    if task_today is None:
        print('No task for today.')
        return

    # Prepare Bible.
    bible = Bible()

    # Get the verses and footnotes
    try:
        # Try to fetch from bible gateway first.
        (verses, footnotes) = get_data_from_bible_gateway(task_today, bible)
    except Exception as e:
        # If failed to fetch from bible gateway, use local Bible data.
        print(f'Failed to fetch BibleGateway for task: {task_today}, {e}')
        print('Using fallback instead')

        verses = get_verses_from_fallback(task_today, bible)
        footnotes = None

    # The message to be sent
    telegram_message = format_telegram_message(
        task=task_today,
        verses=verses,
        footnotes=footnotes
    )

    # Get all subscribers
    subscribers = get_subscribers(db)

    # Exit if there are no subscribers
    if len(subscribers) == 0:
        print('No subscribers to send')
        return

    # Get access to the bot
    bot = telegram.Bot(token=TOKEN)

    # Send the message to all subscribers
    for chat_id in subscribers:
        # Send message every 4000 characters, this is telegram's limitation.
        for i in range(0, len(telegram_message), 4000):
            sub_message = telegram_message[i:i+4000]

            bot.send_message(
                chat_id=chat_id,
                text=sub_message,
                parse_mode=telegram.ParseMode.HTML
            )

    print(f'Successfully sent messages to {len(subscribers)} subscriber(s)')


if __name__ == "__main__":
    main()
