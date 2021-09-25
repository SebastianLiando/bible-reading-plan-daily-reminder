from ..utils import get_test_asset_content, get_expected_footnotes
from bible.bible_gateway import BibleGatewayParser, BibleGateway
import requests_mock


def assert_footnotes_and_contents(source: str, expected: str, footnote: str):
    raw = get_test_asset_content(source)

    parser = BibleGatewayParser(raw)

    # Check footnotes
    footnotes = parser.get_footnotes()
    expected_footnotes = get_expected_footnotes(footnote)

    assert footnotes == expected_footnotes

    # Check formatted verses
    expected_content = get_test_asset_content(expected)
    content = parser.get_formatted_verses()

    assert content == expected_content


def test_colossians_3():
    assert_footnotes_and_contents(
        'col-3.txt',
        'col-3_expected.txt',
        'col-3_footnotes.txt'
    )


def assert_url(expected: str, book: str, chapter: int, version: str = 'NIV'):
    gateway = BibleGateway()
    url = gateway.get_url(book, chapter, version)

    assert url == expected


def test_get_url_for_single_word_book():
    assert_url(
        'https://www.biblegateway.com/passage/?search=colossians+3&version=NIV',
        'colossians', 3
    )


def test_get_url_for_multi_word_book():
    assert_url(
        'https://www.biblegateway.com/passage/?search=1%20Timothy+3&version=NIV',
        '1 Timothy', 3
    )


def test_get_html_calls_get_request_with_correct_url():
    book, chapter = 'colossians', 3

    gateway = BibleGateway()
    url = gateway.get_url(book, chapter)

    # Mock the HTML call, so that it returns the URL as a response
    with requests_mock.Mocker() as mock:
        mock.get(url, text=url)
        response = gateway.get_html(book, chapter)

    assert response == url
