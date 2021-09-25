from bible.utils import get_superscript


def test_superscript_zero():
    assert get_superscript(0) == '⁰'


def test_superscript_multiple_digit():
    assert get_superscript(12) == '¹²'
