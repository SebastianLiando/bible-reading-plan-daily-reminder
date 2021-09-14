from datetime import datetime
from src.assets import get_asset
from src.bible import Bible, PlanManager
from src.token import TOKEN

import telegram

import csv

from src.utils import get_superscript

# Read reading plan data.
rows = []
with open(get_asset('plan.csv')) as file:
    reader = csv.reader(file)

    # Exclude header
    rows = list(reader)[1:]
plan_manager = PlanManager(rows)

# Get today's reading plan.
task_today = plan_manager.get_task_at(date=datetime(2021, 9, 20).date())

# Prepare Bible.
bible = Bible()

# Get verses for today.
today_verses = bible.get_verses_from_chapter(
    task_today.book,
    task_today.chapter,
    task_today.start_verse,
    task_today.end_verse
)

# Add the verse numbers to each verse.
for i in range(0, len(today_verses)):
    verse_no = get_superscript(i + 1)

    today_verses[i] = f"{verse_no} {today_verses[i]}"

# Which chapter and book the verses are from
reading_chapter = f'📚<b>{task_today.book.upper()} {task_today.chapter}</b>'

# Join the verses into a single string.
verses = '\n'.join(today_verses)

# The message lines to be send by telegram bot.
message_lines = [
    "Hi friends 🖐! Here's the reading plan for today.",
    '\n',
    reading_chapter,
    verses
]

# Start the bot
bot = telegram.Bot(token=TOKEN)
bot.send_message(
    chat_id=278794854,
    text='\n'.join(message_lines),
    parse_mode=telegram.ParseMode.HTML
)