from datetime import date, datetime
from typing import List, Optional, Set
from google.cloud import firestore
from src.bible.plan_manager import ReadingTask
from src.data.plan_repository import PlanRepository
from src.data.subscriber_repository import SubscriberRepository
from src.bible.bible import Bible
from src.token import TOKEN
from src.utils import get_superscript

import telegram


def get_date_today() -> date:
    """Return today's date. The timezone is based on the system region.

    Returns:
        date: The date of today.
    """
    return datetime.now().date()


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


def get_subscribers(db: firestore.Client) -> Set[str]:
    """Returns subscriber ids from firestore.

    Args:
        db (firestore.Client): The firestore client.

    Returns:
        Set[str]: Subscribers' telegram chat ids.
    """
    repo = SubscriberRepository(db)

    return repo.get_subscribers()


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

    # Get verses for today.
    today_verses = get_verses_from_reading_task(bible, task_today)

    # Format the verses nicely
    verses = beautify_verses(today_verses)

    # Which chapter and book the verses are from
    reading_chapter = f'📚<b>{task_today.book.upper()} {task_today.chapter} (NIV84)</b>📚'

    # The message lines to be sent.
    message_lines = [
        "Hi friends 🖐! Here's the reading plan for today.",
        '\n',
        reading_chapter,
        verses
    ]
    # The message to be sent
    telegram_message = '\n'.join(message_lines)

    # Get all subscribers
    subscribers = get_subscribers(db)

    if len(subscribers) == 0:
        print('No subscribers to send')
        return

    # Get access to the bot
    bot = telegram.Bot(token=TOKEN)

    # Send the message to all subscribers
    for chat_id in subscribers:
        bot.send_message(
            chat_id=chat_id,
            text=telegram_message,
            parse_mode=telegram.ParseMode.HTML
        )

    print(f'Successfully sent messages to {len(subscribers)} subscriber(s)')


if __name__ == "__main__":
    main()
