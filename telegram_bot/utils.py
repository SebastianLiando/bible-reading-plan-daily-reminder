from time import strftime
from datetime import date, datetime
from typing import Optional, Set
from google.cloud import firestore

from data.subscriber_repository import SubscriberRepository, SubscriptionItem
from data.plan_repository import PlanRepository
from bible.plan_manager import ReadingTask
from bible.bible_gateway import BibleGateway
from telegram_bot.daily_message_manager import TaskMessageManager


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


def get_subscribers_chat_ids(item: SubscriptionItem) -> Set[str]:
    """Returns subscriber ids from firestore for the given item..

    Args:
        item (SubscriptionItem): Which subscription the chat should be subscribed to.

    Returns:
        Set[str]: Subscribers' telegram chat ids.
    """
    repo = SubscriberRepository()
    subs = repo.list_by_subscription(item)

    ids = map(lambda sub: sub.chat_id, subs)

    return set(ids)


def format_telegram_message(task: ReadingTask, body: str) -> str:
    # Today's date, formatted
    today_date = f'📅 <b>{format_date_today(get_date_today())}</b>'

    # Reading plan, formatted
    reading_chapter = f'{task.book.upper()} {task.chapter}'
    reading_plan = f'📖 <b>{reading_chapter}</b>'

    # Credit link to Bible Gateway
    source_url = BibleGateway().get_url(task.book, task.chapter)
    credit_section = f'See from source: <a href="{source_url}">Bible Gateway</a>'

    # The message lines to be sent.
    message_lines = [
        today_date,
        reading_plan,
        '\n',
        body,
        '\n',
        credit_section,
    ]

    return '\n'.join(message_lines)


def get_message_for_today(db: firestore.Client, message_manager: TaskMessageManager = TaskMessageManager()) -> Optional[str]:
    """Returns the telegram message for today's task.

    Args:
        db (firestore.Client): The firestore client.
        message_manager (TaskMessageManager, optional): The task message manager. Defaults to TaskMessageManager().

    Returns:
        Optional[str]: The telegram message for today's task.
    """
    # Get today's reading plan.
    task_today = get_today_reading_plan(db)

    # If there is no plan for today, the task ends
    if task_today is None:
        return None

    # Get the content for today
    body = message_manager.get_task_message(task_today)

    # Format the message to be sent
    return format_telegram_message(
        task=task_today,
        body=body
    )
