from typing import Dict, List, Tuple
from bs4 import BeautifulSoup
from bs4.element import Tag
import requests

BASE_URL = 'https://www.biblegateway.com/passage'


class BibleGateway:
    def get_url(self, book: str, chapter: int, version: str = 'NIV') -> str:
        # Replace whitespace with %20, which is used for URLs
        book_parsed = book.replace(" ", "%20")

        # Add the query parameters
        return BASE_URL + f'/?search={book_parsed}+{chapter}' + f'&{version}'

    def get_html(self, book: str, chapter: int, version: str = 'NIV') -> str:
        result = requests.get(self.get_url(book, chapter, version))
        print('Fetching from ' + result.url)

        # Throw error if not successful
        result.raise_for_status()

        return result.text


class BibleGatewayParser:
    def __init__(self, raw_html: str) -> None:
        self.raw_html = raw_html

    def get_footnotes(self) -> List[Tuple[str, str]]:
        """Returns the footnotes for the passage. The first is the verse and the second is the 
        footnote.

        Returns:
            List[Tuple[str, str]]: The first is the verse and the second is the footnote.
        """
        soup = BeautifulSoup(raw, 'html.parser')
        result = []

        footnotes_section = soup.find('div', class_='footnotes')

        if not footnotes_section is None:
            # Find all footnotes list items
            o_list = footnotes_section.find('ol')
            footnotes = [] if o_list is None else o_list.find_all('li')

            for footnote in footnotes:
                # Get which verse the footnote is for
                verse = footnote.find('a').text

                # Get the footnote content, here we use inner HTML.
                # Telegram supports enough for this HTML format, see https://core.telegram.org/bots/api#html-style
                content = footnote.find('span').decode_contents()
                # Remove the span inside italic (e.g. in Exodus 3)
                content = content.replace('</span>', '') \
                    .replace('<span class="small-caps">', '')

                # Footnote can contain nested HTML tags, so use this first
                # content = footnote.find('span').text
                result.append((verse, content))

        return result


gateway = BibleGateway()
raw = gateway.get_html('Exodus', 6)

parser = BibleGatewayParser(raw)
for (k, v) in parser.get_footnotes():
    print(f'{k} -> {v}')
