from typing import List
from datetime import date, datetime
from time import strftime, strptime

from google.cloud.firestore_v1.base_document import DocumentSnapshot

DATE_FORMAT = '%d-%b-%y'

# Data class that contains information about the reading task for a particular day.


class ReadingTask:
    def __init__(self, book: str, chapter: int, start_verse: int, end_verse: int, date: date) -> None:
        self.book = book
        self.chapter = chapter
        self.start_verse = start_verse
        self.end_verse = end_verse
        self.date = date

    def to_dict(self) -> dict:
        return {
            'book': self.book,
            'chapter': self.chapter,
            'start_verse': self.start_verse,
            'end_verse': self.end_verse,
            'date': to_csv_date(self.date)
        }

    @staticmethod
    def from_doc(doc: DocumentSnapshot):
        """Create a ReadingTask object from firestore document.

        Args:
            doc (DocumentSnapshot): The firestore document.

        Returns:
            ReadingTask: the reading task.
        """
        content = doc.to_dict()

        return ReadingTask(
            content['book'],
            content['chapter'],
            content['start_verse'],
            content['end_verse'],
            parse_csv_date(content['date'])
        )

    def __str__(self) -> str:
        return str(self.to_dict())


def to_csv_date(date: date) -> str:
    return strftime(DATE_FORMAT, date.timetuple())


def parse_csv_date(date_str: str) -> date:
    parsed_date = strptime(date_str, DATE_FORMAT)

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
            chapter = int(plan[2])

            # Verse range
            # If both are empty string -> all the verse
            start_verse = -1 if plan[3] == '' else int(plan[3])
            end_verse = 1000 if plan[4] == '' else int(plan[4])

            self.reading_tasks[plan_date] = ReadingTask(
                book, chapter, start_verse, end_verse, plan_date
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
