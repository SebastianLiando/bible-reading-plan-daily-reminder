from datetime import datetime, timedelta
from typing import Dict, List, Optional

from bible.plan_manager import ReadingTask
from bible.bible import Bible


class ScheduleParser:
    def __init__(self, csv_data: List[List[str]], start_date: datetime, bible: Bible, expected_headers: List[str] = []) -> None:
        self.schedule = {}

        # Validate the header
        if len(expected_headers) != 0:
            headers = csv_data[0]
            if headers != expected_headers:
                raise ValueError(
                    f"Unexpected header! Found {headers}, expected {expected_headers}")

        # Remove header
        csv_data = csv_data[1:]

        # Begin parsing schedule
        current_book = None
        current_date = start_date

        for row in range(len(csv_data)):
            csv_data[row] = csv_data[row][2:]  # Remove date and week number
            csv_data[row] = csv_data[row][:7]  # Remove remarks

            for col in range(len(csv_data[row])):
                cell_data = csv_data[row][col].strip()
                space_index = cell_data.rfind(" ")
                chapter_no = None

                if cell_data != '':
                    # If a new book is introduced
                    if space_index != -1:
                        book = cell_data[:space_index].strip()
                        book = bible.fuzzy_search_book(book)
                        current_book = book
                        chapter_no = int(cell_data[space_index+1:])
                    else:
                        chapter_no = int(cell_data)

                    date = current_date.date()
                    self.schedule[date] = ReadingTask(
                        book=current_book, chapter=chapter_no, date=date,
                        start_verse=1, end_verse=1000)

                current_date = current_date + timedelta(days=1)

    def get_tasks(self, start_date: datetime, end_date: Optional[datetime] = None) -> List[ReadingTask]:
        result = []
        start = start_date.date()
        end = None if end_date is None else end_date.date()

        for date in self.schedule.keys():
            task = self.schedule[date]

            if end is None:
                if date >= start:
                    result.append(task)
            else:
                if date >= start and date <= end:
                    result.append(task)

        return result
