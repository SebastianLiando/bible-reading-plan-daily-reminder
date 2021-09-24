from typing import List, Tuple
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from . import utils
import requests

BASE_URL = 'https://www.biblegateway.com/passage'


def is_html_tag(test, name: str) -> bool:
    return isinstance(test, Tag) and test.name == name


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
        soup = BeautifulSoup(self.raw_html, 'html.parser')
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

    def _extract_header(self, header: Tag) -> str:
        header_span = header.find('span')
        header_text = list(header_span.children)[0]

        return f'<b>{header_text}</b>'

    def _extract_paragraph(self, p: Tag) -> str:
        verses_in_paragraph = ''

        spans = filter(lambda x: is_html_tag(x, 'span'), p.children)

        for span in spans:
            for content in span.children:
                # If the current content is a verse number or footnote.
                # Verse number -> it is in a <sup class="versenum">.
                # Footnote -> it is in a <sup class="footnote">.
                if is_html_tag(content, 'sup'):
                    sup_class = content.get('class')

                    if 'versenum' in sup_class:
                        # Verse number
                        verse_num = int(content.text)
                        verses_in_paragraph += f' <b>{utils.get_superscript(verse_num)}</b> '
                    elif 'footnote' in sup_class:
                        # Footnote
                        verses_in_paragraph += f'<i>{content.text}</i>'

                # If it is a part of the verse
                elif isinstance(content, NavigableString):
                    verses_in_paragraph += content.text

                # If it is a part of the verse, but within a <span class="small-caps"
                elif is_html_tag(content, 'span') and 'small-caps' in content.get('class', []):
                    verses_in_paragraph += content.text

        return verses_in_paragraph

    def get_formatted_verses(self) -> str:
        soup = BeautifulSoup(self.raw_html, 'html.parser')

        result_lines = []
        std_text = soup.find('div', class_='std-text')

        for child in std_text.children:
            if is_html_tag(child, 'h3'):
                # This is header
                result_lines.append(self._extract_header(child))
            elif is_html_tag(child, 'p'):
                # This is <p>, contains <span> elements
                result_lines.append(self._extract_paragraph(child))

        return '\n\n'.join(result_lines)