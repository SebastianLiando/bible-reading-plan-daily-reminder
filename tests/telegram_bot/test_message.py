from telegram_bot.message import split_html_message


def test_split_verses():
    message = '<b>¹</b> 11 <b>²</b> 11 <b>³</b> 11'
    expected = ['<b>¹</b> 11 ', '<b>²</b> 11 ', '<b>³</b> 11']

    assert split_html_message(message, length=12) == expected


def test_split_footnotes():
    footnotes = '📝 <b>Footnotes</b>\na. 45\nb. 45\nc. 45\nd. 45'
    expected = ['📝 <b>Footnotes</b>\n', 'a. 45\nb. 45\nc. 45\n', 'd. 45']

    assert split_html_message(footnotes, length=20) == expected
