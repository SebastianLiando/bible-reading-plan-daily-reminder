from ..utils import get_test_asset_content, get_expected_footnotes
from bible.bible_gateway import BibleGatewayParser


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
