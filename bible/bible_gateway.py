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
        return BASE_URL + f'/?search={book_parsed}+{chapter}' + f'&version={version}'

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

                # Get the footnote content.
                # Telegram supports enough for this HTML format, see https://core.telegram.org/bots/api#html-style
                content_span = footnote.find('span')
                content = self._extract_span(content_span)

                # Footnote can contain nested HTML tags, so use this first
                # content = footnote.find('span').text
                result.append((verse, content))

        return result

    def _extract_header(self, header: Tag) -> str:
        header_span = header.find('span')
        header_text = self._extract_span(header_span)

        return f'<b>{header_text}</b>'

    def _extract_sup(self, sup: Tag) -> str:
        """Extracts the content of <sup> tag.
        - Verse number -> it is in a <sup class="versenum">.
        - Footnote -> it is in a <sup class="footnote">.

        Args:
            sup (Tag): The <sup> tag

        Returns:
            str: The text of the <sup> tag.
        """
        tag_classes = sup.get('class', [])
        text = sup.text

        if 'versenum' in tag_classes:
            # Verse number
            return self._format_verse_num(text)
        elif 'footnote' in tag_classes:
            # Footnote indicator
            return f'<i>{text}</i>'
        else:
            # Ignore other <sup> tags
            return ''

    def _extract_span(self, span: Tag) -> str:
        """Recursively extract the content text of the <span> tag.

        Args:
            span (Tag): The span tag.

        Returns:
            str: The extracted text.
        """
        children = list(span.children)

        # Base case
        if len(children) == 1 and isinstance(children[0], NavigableString):
            tag_class = span.get('class', [])

            if 'small-caps' in tag_class:
                return children[0].text.upper()
            else:
                return children[0].text

        result = ''

        # Else, iterate and extract
        for child in children:
            child_text = child.text

            if isinstance(child, NavigableString):
                result += child_text
            elif is_html_tag(child, 'sup'):
                result += self._extract_sup(child)
            elif is_html_tag(child, 'span') and not 'chapternum' in child.get('class', []):
                result += self._extract_span(child)
            elif is_html_tag(child, 'i'):
                result += f'<i>{child_text}</i>'

        return result

    def _extract_poetry(self, div: Tag) -> str:
        result = ''

        p = div.find('p')
        for child in p.children:
            if is_html_tag(child, 'br'):
                result += '\n'
            elif is_html_tag(child, 'span'):
                result += self._extract_span(child)

        return result

    def _format_verse_num(self, num: str) -> str:
        num_chars = filter(lambda c: c.isnumeric(), num)
        number = int(''.join(num_chars))
        return f' <b>{utils.get_superscript(number)}</b> '

    def _extract_paragraph(self, p: Tag) -> str:
        verses_in_paragraph = ''

        spans = filter(lambda x: is_html_tag(x, 'span'), p.children)

        for span in spans:
            verses_in_paragraph += self._extract_span(span)

        return verses_in_paragraph

    def extract_verses(self, from_verse: int = 1, to_verse: int = -1) -> str:
        """Returns the verses as formatted like in Bible Gateway.

        Args:
            from_verse (int, optional): Which verse number to start from. Defaults to 1.
            to_verse (int, optional): Which verse number to end. Defaults to -1, meaning until end. This
            number must be larger or equal to `from_verse`. 

        Returns:
            str: The verses.
        """
        soup = BeautifulSoup(self.raw_html, 'html.parser')

        result_lines = []
        std_text = soup.find('div', class_='std-text')

        for child in std_text.children:
            if is_html_tag(child, 'h3') or is_html_tag(child, 'h4'):
                # This is header
                result_lines.append(self._extract_header(child))
            elif is_html_tag(child, 'p'):
                # This is <p>, contains <span> elements
                result_lines.append(self._extract_paragraph(child))
            elif is_html_tag(child, 'div') and 'poetry' in child.get('class', []):
                # If it is a poetry
                result_lines.append(self._extract_poetry(child))
            elif is_html_tag(child, 'div'):
                # John 17 use this structure as paragraph
                paragraphs = child.findChildren('p')
                for p_child in paragraphs:
                    result_lines.append(self._extract_paragraph(p_child))

        result = '\n\n'.join(result_lines)

        # Perform cutting if needed
        if from_verse > 1:
            verse_num_str = self._format_verse_num(str(from_verse))
            target = result.find(verse_num_str)

            # If the target is valid, then cut the verse
            if target != -1:
                result = result[target:]

        if to_verse != -1 and to_verse >= from_verse:
            verse_num_str = self._format_verse_num(str(to_verse + 1))
            target = result.find(verse_num_str)

            # If it the end target is valid, then cut the verse
            if target != -1:
                result = result[:target]

        return result
