from datetime import datetime
import requests
import csv
from io import StringIO
from google.cloud import firestore
from bible.bible import Bible
from data import db
from data.plan_repository import PlanRepository
from config.env import GOOGLE_SHEET_TASK_URL, GOOGLE_SHEET_TASK_HEADERS, CREDENTIALS

from schedule.schedule_parser import ScheduleParser


def main():
    START_YEAR = 2022
    URL = f'{GOOGLE_SHEET_TASK_URL}/export?format=csv'

    print('Downloading reading task schedule as CSV from ' + URL)
    response = requests.get(URL)
    response.raise_for_status()

    # Convert schedule to 2D list
    content = response.text
    content_stream = StringIO(content)
    reader = csv.reader(content_stream)
    csv_data = list(reader)

    current_date = datetime(START_YEAR, 1, 3)
    bible = Bible()
    schedule_parser = ScheduleParser(csv_data, current_date, bible,
                                     expected_headers=GOOGLE_SHEET_TASK_HEADERS)
    print('Successfully parsed tasks from google sheet!')

    today = datetime.now()
    print(f'Retrieving tasks from {today.date()} onwards.')
    tasks = schedule_parser.get_tasks(start_date=today)

    print(f'Uploading {len(tasks)} tasks.')
    
    task_repo = PlanRepository(db)
    i = 0
    for task in tasks:
        task_repo.upsert_plan(task)
        i += 1
        print(f'\r{i} / {len(tasks)}', end='')

    print()
    print('Upload task complete!')


if __name__ == '__main__':
    main()
