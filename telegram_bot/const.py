from typing import Optional
from eventbrite import FALLBACK_URL
from telegram_bot.env import BASE_URL, PORT
from telegram_bot.bot_manager import BotWebhookSettings


WEBHOOK_SETTINGS = BotWebhookSettings(
    listen_ip='0.0.0.0',
    port=PORT,
    base_url=BASE_URL
)

CALLBACK_DATA_CANCEL = '-1'

BUTTON_SUBSCRIBE = 'Subscribe'
BUTTON_UNSUBSCRIBE = 'Unsubscribe'
BUTTON_CANCEL = 'Cancel'

STATUS_SUBSCRIBED = '<b>Subscribed</b>'
STATUS_UNSUBSCRIBED = '<b>Unsubscribed</b>'

LABEL_WELCOME = 'Hi there 👋 Welcome to the daily reminder bot.'
LABEL_SUBSCRIPTION_STATUS = 'Status: '
LABEL_USER_NO_PRIVILEGE = 'Only admin and owner can change subscription.'
LABEL_CANCEL_OPERATION = 'You have canceled the operation.'
LABEL_SUBSCRIBED = 'This chat is now subscribed to the daily reminder.'
LABEL_UNSUBSCRIBED = 'This chat is no longer subscribed to the daily reminder.'


def _build_subscription_status(subscribed: bool) -> str:
    if subscribed:
        return LABEL_SUBSCRIPTION_STATUS + STATUS_SUBSCRIBED
    else:
        return LABEL_SUBSCRIPTION_STATUS + STATUS_UNSUBSCRIBED


def build_button_label(subscribed: bool) -> str:
    if subscribed:
        return BUTTON_UNSUBSCRIBE
    else:
        return BUTTON_SUBSCRIBE


def build_subscription_change_message(subscribed: bool) -> str:
    if subscribed:
        return LABEL_SUBSCRIBED
    else:
        return LABEL_UNSUBSCRIBED


def build_start_message(subscribed: bool, authorized: bool) -> str:
    lines = [
        LABEL_WELCOME,
        _build_subscription_status(subscribed),
    ]

    if not authorized:
        lines.append(LABEL_USER_NO_PRIVILEGE)

    return '\n'.join(lines)


# ------------------------ Service Reminder
_SERVICE_REMINDER_MESSAGE_TEMPLATE = '''⏰ Gentle reminder to register for this week\'s sermon!

If you haven't <b><a href = "{}">click here to register now.</a></b>

<i>If the above link doesn't work, <a href="{}">click here</a> instead.</i>
'''
_FALLBACK_SERVICE_REMINDER = f'''⏰ Gentle reminder to register for this week\'s sermon!

If you haven't <b><a href = "{FALLBACK_URL}">click here to register now.</a></b>'''


def build_service_reminder(url: Optional[str]) -> str:
    if url is None:
        return _FALLBACK_SERVICE_REMINDER
        
    return _SERVICE_REMINDER_MESSAGE_TEMPLATE.format(url, FALLBACK_URL)
