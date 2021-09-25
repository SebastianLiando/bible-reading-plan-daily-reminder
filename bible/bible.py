import xml.etree.ElementTree as ElementTree
from fuzzywuzzy import fuzz
from assets import get_asset
from typing import List, Tuple


class Bible:
    def __init__(self, asset_name: str = 'niv.xml') -> None:
        # Get the XML file path.
        asset_path = get_asset(asset_name)

        # Parse the XML path
        tree = ElementTree.parse(asset_path)
        root = tree.getroot()

        self.content = {}

        for book in root.iterfind('book'):
            book_name = book.get('name').lower()
            self.content[book_name] = {}

            for chapter in book.iterfind('chapter'):
                chapter_no = chapter.get('name')
                self.content[book_name][chapter_no] = {}

                for verse in chapter.iterfind('verse'):
                    verse_no = verse.get('name')

                    self.content[book_name][chapter_no][verse_no] = verse.text

    def fuzzy_search_book(self, query: str) -> str:
        '''
        Returns the bible book name that best matches the query.
        '''
        books = self.content.keys()
        scores = {}

        for book in books:
            score = fuzz.partial_ratio(book, query.lower())
            scores[book] = score

        best_score = max(scores.values())

        # Best matches for the given query
        books_with_best_score = []

        for book in books:
            if scores[book] == best_score:
                books_with_best_score.append(book)

        # Create a list of books with the length of the title
        books_and_length = map(
            lambda title: (len(title), title),
            books_with_best_score
        )

        # Sort the book by the title length first, then lexicographically
        sorted_books = sorted(books_and_length)
        # print(sorted_books)

        # Return the book name of the first item
        return sorted_books[0][1]

    def parse_book_chapter_verse(self, input_str: str) -> Tuple[str, str, str]:
        '''
        Returns the book name, the chapter number, and the verse number from the given input string.
        '''
        # Split by whitespace
        parts = input_str.split(" ")

        # Verse number is the last part
        verse_no = parts[len(parts) - 1]

        # Chapter number is before the verse number
        chapter_no = parts[len(parts) - 2]

        # The rest of the part is the book name
        book = " ".join(parts[0:len(parts) - 1])
        book_name = self.fuzzy_search_book(book)

        return (book_name, chapter_no, verse_no)

    def get_verses_from_chapter(self, book: str, chapter: str, start: int, end: int) -> List[str]:
        '''
        Returns a list of verses from the chosen book and chapter.
        '''
        # Ensure the book exists
        book_name = self.fuzzy_search_book(book)

        # Get all the verses from the book and chapter
        verses: dict = self.content[book_name][str(chapter)]

        # Get the number of verses available
        verse_nums = map(int, verses.keys())
        last_verse_num = max(verse_nums)

        # Add the verses that satisfies the range
        result = []

        for i in range(1, last_verse_num + 1):
            if i >= start and i <= end:
                result.append(verses[str(i)])

        return result
