from ast import dump
from telegram.chat import Chat
from telegram.constants import CHAT_CHANNEL, CHAT_PRIVATE, CHATMEMBER_ADMINISTRATOR, CHATMEMBER_CREATOR, PARSEMODE_HTML
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.user import User
from telegram_bot.const import BUTTON_CANCEL, CALLBACK_DATA_CANCEL, build_button_label, build_start_message
from data import db
from data.subscriber_repository import Subscriber, SubscriberRepository, SubscriptionItem
from telegram import Update
import json

repo = SubscriberRepository(db)


def toggle_subscription(id: str, item: SubscriptionItem) -> bool:
    updated = repo.toggle_subscription(id, item)
    return updated.is_subscribed_to(item)


def reply_unauthorized_start(chat_id: str, update: Update):
    subscriber = repo.get(chat_id)
    if subscriber is None:
        subscriber = Subscriber(id='', chat_id=chat_id, sub_items=set())

    message = build_start_message(subscriber, authorized=False)

    update.effective_chat.send_message(
        text=message,
        parse_mode=PARSEMODE_HTML
    )


def reply_authorized_start(chat_id: str, update: Update):
    # Get subscriber data for the chat
    subscriber = repo.get(chat_id)
    if subscriber is None:
        subscriber = Subscriber(id='', chat_id=chat_id, sub_items=set())

    # Create inline buttons
    buttons = []

    all_reminders = SubscriptionItem.values(sort=True)
    for reminder in all_reminders:
        # Check if subscribed
        subscribed = subscriber.is_subscribed_to(reminder)

        # Create the toggle button
        button_label = build_button_label(subscribed, reminder)
        callback_data = {
            'chat_id': chat_id,
            'sub_item': reminder.value
        }
        button = InlineKeyboardButton(
            text=button_label,
            callback_data=json.dumps(callback_data)
        )

        buttons.append(button)

    cancel_button = InlineKeyboardButton(
        text=BUTTON_CANCEL,
        callback_data=CALLBACK_DATA_CANCEL
    )
    buttons.append(cancel_button)

    keyboard = [[button] for button in buttons]  # 1 button per line

    # Send the message
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = build_start_message(subscriber, authorized=True)

    update.effective_chat.send_message(
        text=message,
        reply_markup=reply_markup,
        parse_mode=PARSEMODE_HTML
    )


def is_sender_authorized(chat: Chat, sender: User) -> bool:
    """Checks if the user is allowed to call privileged commands. 
    User is always authorized in their private message with the bot. For channels and groups, the user
    must be either the owner or an admin.

    Args:
        chat (Chat): The chat.
        sender (User): The user that wants to modify the subscription.

    Returns:
        bool: `True` if the user is allowed to modify.
    """

    # Private chat is authorized, since it is only 1 user.
    # Channel chat is authorized, because only admins can send message.
    if chat.type in [CHAT_PRIVATE, CHAT_CHANNEL]:
        return True

    # For group and supergroups, check that the sender is an admin or the owner.
    member = chat.get_member(sender.id)

    return member.status in [CHATMEMBER_ADMINISTRATOR, CHATMEMBER_CREATOR]
