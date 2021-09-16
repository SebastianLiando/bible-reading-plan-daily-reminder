from typing import List
from datetime import date, datetime
from time import strftime, strptime

from google.cloud.firestore import DocumentSnapshot

DATE_FORMAT = '%d-%b-%y'


def to_csv_date(date: date) -> str:
    """Converts date to the date format in the CSV.

    Args:
        date (date): The date to con

    Returns:
        str: The formatted date.
    """
    return strftime(DATE_FORMAT, date.timetuple())


def parse_csv_date(date_str: str) -> date:
    """Parse the string into a date object. The string must follow the format in the CSV (e.g. 18-Sep-21).

    Args:
        date_str (str): The date string.

    Returns:
        date: The date object.
    """
    parsed_date = strptime(date_str, DATE_FORMAT)

    return datetime(
        year=parsed_date.tm_year,
        month=parsed_date.tm_mon,
        day=parsed_date.tm_mday).date()


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

    def get_tasks(self) -> List[ReadingTask]:
        """Returns all reading tasks.

        Returns:
            List[ReadingTask]: All reading tasks.
        """
        return list(self.reading_tasks.values())
