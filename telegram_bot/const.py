from typing import Optional
from data.subscriber_repository import Subscriber, SubscriptionItem
from eventbrite import FALLBACK_URL
from telegram_bot.env import BASE_URL, PORT
from telegram_bot.bot_manager import BotWebhookSettings


WEBHOOK_SETTINGS = BotWebhookSettings(
    listen_ip='0.0.0.0',
    port=PORT,
    base_url=BASE_URL
)

CALLBACK_DATA_CANCEL = '-1'

BUTTON_SUBSCRIBE = 'Subscribe to "{}"'
BUTTON_UNSUBSCRIBE = 'Unsubscribe from "{}"'
BUTTON_CANCEL = 'Cancel'

STATUS_SUBSCRIBED = '<b>Subscribed</b>'
STATUS_UNSUBSCRIBED = '<b>Unsubscribed</b>'


WELCOME_TEMPLATE = '''Hi there 👋 Welcome to the JCC reminder bot.

Currently, there are {} available reminders:
{}
'''
LABEL_SUBSCRIPTION_STATUS = '''This chat's subscription status:
{}
'''
LABEL_USER_NO_PRIVILEGE = 'Only admin and owner can change subscription.'
LABEL_CANCEL_OPERATION = 'You have canceled the operation.'
LABEL_SUBSCRIBED = 'This chat is now subscribed to "{}".'
LABEL_UNSUBSCRIBED = 'This chat is no longer subscribed to "{}".'


def get_sub_icon(subbed: bool) -> str:
    return '🔔' if subbed else '🔕'


def available_reminders_message() -> str:
    all_reminders = SubscriptionItem.values(sort=True)
    all_reminders = list(map(lambda e: f'• {e.short_summary}', all_reminders))

    return '\n'.join(all_reminders)


def subscriptions_status_message(is_subscribed) -> str:
    all_reminders = SubscriptionItem.values(sort=True)
    all_reminders = list(
        map(lambda e: f'{get_sub_icon(is_subscribed(e))} {e.label}', all_reminders))
    joined = '\n'.join(all_reminders)

    return LABEL_SUBSCRIPTION_STATUS.format(joined)


def build_button_label(subscribed: bool, item: SubscriptionItem) -> str:
    if subscribed:
        return BUTTON_UNSUBSCRIBE.format(item.label)
    else:
        return BUTTON_SUBSCRIBE.format(item.label)


def build_subscription_change_message(subscribed: bool, item: SubscriptionItem) -> str:
    if subscribed:
        return LABEL_SUBSCRIBED.format(item.label)
    else:
        return LABEL_UNSUBSCRIBED.format(item.label)


def build_start_message(subscriber: Subscriber, authorized: bool) -> str:
    lines = [
        WELCOME_TEMPLATE.format(
            len(SubscriptionItem.values()),  # How many reminders
            available_reminders_message(),  # Brief summary of reminders
        ),
        subscriptions_status_message(
            lambda item: subscriber.is_subscribed_to(item))
    ]

    if not authorized:
        lines.append(LABEL_USER_NO_PRIVILEGE)

    return '\n'.join(lines)


# ------------------------ Service Reminder
_SERVICE_REMINDER_MESSAGE_TEMPLATE = '''⏰ Gentle reminder to register for this week\'s service!

If you haven't <b><a href = "{}">click here to register now.</a></b>

<i>If the above link doesn't work, <a href="{}">click here</a> instead.</i>
'''
_FALLBACK_SERVICE_REMINDER = f'''⏰ Gentle reminder to register for this week\'s service!

If you haven't <b><a href = "{FALLBACK_URL}">click here to register now.</a></b>'''


def build_service_reminder_message(url: Optional[str]) -> str:
    if url is None:
        return _FALLBACK_SERVICE_REMINDER

    return _SERVICE_REMINDER_MESSAGE_TEMPLATE.format(url, FALLBACK_URL)
