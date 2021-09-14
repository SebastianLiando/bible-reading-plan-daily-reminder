from typing import List
from datetime import date, datetime
from time import strptime


# Data class that contains information about the reading task for a particular day.
class ReadingTask:
    def __init__(self, book, chapter, start_verse, end_verse) -> None:
        self.book: str = book
        self.chapter: str = chapter
        self.start_verse: int = start_verse
        self.end_verse: int = end_verse

    def __str__(self) -> str:
        parts = [
            f'book: {self.book}',
            f'chapter: {self.chapter}',
            f'start_verse: {self.start_verse}',
            f'end_verse: {self.end_verse}'
        ]
        return f"({', '.join(parts)})"


def parse_csv_date(date_str: str) -> date:
    parsed_date = strptime(date_str, '%d-%b-%y')

    return datetime(
        year=parsed_date.tm_year,
        month=parsed_date.tm_mon,
        day=parsed_date.tm_mday).date()


class PlanManager:
    def __init__(self, plans: List[List[str]]) -> None:
        self.reading_tasks = {}

        for plan in plans:
            # Parse the date
            plan_date = parse_csv_date(plan[0])

            # Book
            book = plan[1]

            # Chapter number
            chapter = plan[2]

            # Verse range
            # If both are empty string -> all the verse
            start_verse = -1 if plan[3] == '' else int(plan[3])
            end_verse = 1000 if plan[4] == '' else int(plan[4])

            self.reading_tasks[plan_date] = ReadingTask(
                book, chapter, start_verse, end_verse
            )

    def get_task_at(self, date: date) -> ReadingTask:
        '''
        Returns the reading task for the given date.
        '''
        return self.reading_tasks.get(date)

    def get_task_today(self) -> ReadingTask:
        '''
        Returns the reading task for the system's current date.
        '''
        current_date = datetime.now().date()
        return self.get_task_at(current_date)
