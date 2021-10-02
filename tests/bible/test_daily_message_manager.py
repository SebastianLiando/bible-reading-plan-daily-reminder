from datetime import datetime
from pytest_mock import MockFixture
from bible.bible import Bible
from bible.bible_gateway import BibleGateway
from bible.plan_manager import ReadingTask
from telegram_bot.daily_message_manager import TaskMessageManager
from tests.utils import get_test_asset_content

TASK = ReadingTask('', 1, 1, 1000, datetime.now())


def gateway_error(self, book, chapter):
    raise ValueError('Error!')


def bible_get_verse(self, book, chapter, start, end):
    return 'verses'


def test_bible_gateway_success(mocker: MockFixture):
    def gateway_success(self, book, chapter):
        return ''

    mocker.patch('bible.bible_gateway.BibleGateway.get_html', gateway_success)

    def extract_verses(self, from_v, to_v):
        return 'verses'

    mocker.patch(
        'bible.bible_gateway.BibleGatewayParser.extract_verses',
        extract_verses
    )

    def get_footnotes(self):
        return [('from', 'footnote')]

    mocker.patch(
        'bible.bible_gateway.BibleGatewayParser.get_footnotes',
        get_footnotes
    )

    manager = TaskMessageManager()
    spy = mocker.spy(manager, '_get_data_from_bible_gateway')
    manager.get_task_message(TASK)

    assert spy.call_count == 1


def test_bible_gateway_error_fallbacks_to_local_bible(mocker: MockFixture):
    mocker.patch('bible.bible_gateway.BibleGateway.get_html', gateway_error)
    mocker.patch('bible.bible.Bible.get_verses_from_chapter', bible_get_verse)

    bible = Bible()
    spy_bible = mocker.spy(bible, 'get_verses_from_chapter')
    manager = TaskMessageManager(bible=bible)
    manager.get_task_message(TASK)

    assert spy_bible.call_count == 1
