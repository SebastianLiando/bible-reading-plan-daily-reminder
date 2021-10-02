from datetime import date, datetime
from time import strftime
from typing import List, Tuple
from bible.bible import Bible
from bible.bible_gateway import BibleGateway, BibleGatewayParser
from bible.plan_manager import ReadingTask
from bible.utils import get_superscript


def _beautify_verses(verses: List[str], separator: str = '\n') -> str:
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


def _format_footnotes(footnotes: List[Tuple[str, str]]) -> str:
    result = []

    for i in range(len(footnotes)):
        alphabet = chr(ord('a') + i)

        (verse, footnote) = footnotes[i]
        result.append(f'{alphabet}. {verse} - {footnote}')

    return '\n'.join(result)


def _format_verse_footnote(verses: str, footnotes: List[Tuple[str, str]]) -> str:
    # The message lines to be sent.
    message_lines = [verses]

    # Add footnote if any
    if not footnotes is None and len(footnotes) > 0:
        formatted_footnotes = _format_footnotes(footnotes)
        message_lines.append('\n')
        message_lines.append('📝 <b>Footnotes</b>')
        message_lines.append(formatted_footnotes)

    return '\n'.join(message_lines)


class TaskMessageManager:
    def __init__(self,
                 bible: Bible = Bible(),
                 gateway: BibleGateway = BibleGateway()) -> None:
        self.bible = bible
        self.gateway = gateway

    def _get_data_from_bible_gateway(self, task: ReadingTask) -> Tuple[str, List[Tuple[str, str]]]:
        # Get the book name
        book = self.bible.fuzzy_search_book(task.book)

        # Get the chapter number
        chapter = task.chapter

        # Get the verse range
        (start, end) = self.bible.get_verse_range(
            book, chapter,
            task.start_verse, task.end_verse
        )

        # Call bible gateway to get the html source
        raw = self.gateway.get_html(book, chapter)

        # Parse the HTML source
        parser = BibleGatewayParser(raw)

        # Get the verses
        verses = parser.extract_verses(from_verse=start, to_verse=end)

        # Get the footnotes
        footnotes = parser.get_footnotes()

        return (verses, footnotes)

    def _get_verses_from_fallback(self, task: ReadingTask) -> str:
        """Returns the Bible verses from a `ReadingTask` object.

        Args:
            bible (Bible): The Bible.
            task_today (ReadingTask): The reading task for today.

        Returns:
            List[str]: The Bible verses.
        """
        # Get verses for today from local bible.
        today_verses = self.bible.get_verses_from_chapter(
            task.book,
            task.chapter,
            task.start_verse,
            task.end_verse
        )

        # Format the verses nicely
        return _beautify_verses(today_verses)

    def get_task_message(self, task: ReadingTask) -> str:
        try:
            # Try to fetch from bible gateway first.
            (verses, footnotes) = self._get_data_from_bible_gateway(task)
        except Exception as e:
            # If failed to fetch from bible gateway, use local Bible data.
            print(f'Failed to fetch BibleGateway for task: {task}, {e}')
            print('Using fallback instead')

            verses = self._get_verses_from_fallback(task)
            footnotes = None

        return _format_verse_footnote(verses=verses, footnotes=footnotes)
