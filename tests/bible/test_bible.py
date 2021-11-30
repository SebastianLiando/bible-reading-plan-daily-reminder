from bible.bible import Bible
import pytest


@pytest.mark.parametrize('query,expected', [
    ('rev', 'revelation'),
    ('gen', 'genesis'),
    ('gensis', 'genesis'),
    ('mat', 'matthew'),
    ('mak', 'mark'),
    # https://github.com/SebastianLiando/bible-reading-plan-daily-reminder/issues/8
    ('1 john', '1 john'),
    ('john', 'john'),
    ('1 chr', '1 chronicles'),
    ('1 cor', '1 corinthians')
])
def test_fuzzy_search(query, expected):
    actual = Bible().fuzzy_search_book(query)
    assert actual == expected
