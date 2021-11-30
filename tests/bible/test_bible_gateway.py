from ..utils import get_test_asset_content, get_expected_footnotes
from bible.bible_gateway import BibleGatewayParser, BibleGateway
import requests_mock


def assert_footnotes_contents(source: str, expected: str, footnote: str):
    raw = get_test_asset_content(source)

    parser = BibleGatewayParser(raw)

    # Check footnotes
    footnotes = parser.get_footnotes()
    expected_footnotes = get_expected_footnotes(footnote)

    assert footnotes == expected_footnotes

    # Check formatted verses
    expected_content = get_test_asset_content(expected)
    content = parser.extract_verses()

    assert content == expected_content


def assert_cut(source: str, expected: str, from_verse: int = 1, to_verse: int = -1):
    raw = get_test_asset_content(source)

    parser = BibleGatewayParser(raw)

    expected_content = get_test_asset_content(expected)
    content = parser.extract_verses(from_verse=from_verse, to_verse=to_verse)

    assert content == expected_content


def test_colossians_3():
    assert_footnotes_contents(
        'col-3.txt',
        'col-3_expected.txt',
        'col-3_footnotes.txt'
    )


def test_1_timothy_3():
    assert_footnotes_contents(
        '1-timothy-3.txt',
        '1-timothy-3_expected.txt',
        '1-timothy-3_footnotes.txt',
    )


def test_exodus_3():
    assert_footnotes_contents(
        'exodus-3.txt',
        'exodus-3_expected.txt',
        'exodus-3_footnotes.txt'
    )


def test_psalm_1():
    assert_footnotes_contents(
        'psalm-6.txt',
        'psalm-6_expected.txt',
        'psalm-6_footnotes.txt'
    )


def test_psalm_6():
    assert_footnotes_contents(
        'psalm-6.txt',
        'psalm-6_expected.txt',
        'psalm-6_footnotes.txt'
    )

# https://github.com/SebastianLiando/bible-reading-plan-daily-reminder/issues/7


def test_john_17():
    assert_footnotes_contents(
        'john-17.txt',
        'john-17_expected.txt',
        'john-17_footnotes.txt'
    )


# File name that contains the source HTML file to test verse cutting
CUT_TEST_SOURCE_FILE = 'partial.txt'


def test_cutting_from_argument_only():
    assert_cut(
        CUT_TEST_SOURCE_FILE,
        'partial_from.txt',
        from_verse=15
    )


def test_cutting_to_argument_only():
    assert_cut(
        CUT_TEST_SOURCE_FILE,
        'partial_to.txt',
        to_verse=3
    )


def test_cutting_from_and_to_valid():
    assert_cut(
        CUT_TEST_SOURCE_FILE,
        'partial_from_to_valid.txt',
        from_verse=7, to_verse=8
    )


def test_cutting_from_and_to_invalid():
    assert_cut(
        CUT_TEST_SOURCE_FILE,
        'partial_from_to_invalid.txt',
        from_verse=15, to_verse=1
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
