from telegram.chat import Chat
from telegram.constants import CHAT_CHANNEL, CHAT_PRIVATE, CHATMEMBER_ADMINISTRATOR, CHATMEMBER_CREATOR, PARSEMODE_HTML
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.user import User
from telegram_bot.const import BUTTON_CANCEL, CALLBACK_DATA_CANCEL, build_button_label, build_start_message
from data.subscriber_repository import SubscriberRepository
from google.cloud.firestore import Client
from telegram import Update

db = Client()
repo = SubscriberRepository(db)


def _is_user_subscribed(id) -> bool:
    return repo.is_subscribed(str(id))


def toggle_subscription(id: str) -> bool:
    subscribed = _is_user_subscribed(id)

    if not subscribed:
        repo.add_subscriber(id)
    else:
        repo.remove_subscriber(id)

    return not subscribed


def reply_unauthorized(chat_id: str, update: Update):
    subscribed = _is_user_subscribed(chat_id)

    message = build_start_message(subscribed, authorized=False)

    update.effective_chat.send_message(
        text=message,
        parse_mode=PARSEMODE_HTML
    )


def reply_authorized(chat_id: str, update: Update):
    subscribed = _is_user_subscribed(chat_id)
    button_label = build_button_label(subscribed)

    subscription_button = InlineKeyboardButton(
        text=button_label,
        callback_data=str(chat_id)
    )

    cancel_button = InlineKeyboardButton(
        text=BUTTON_CANCEL,
        callback_data=CALLBACK_DATA_CANCEL
    )

    keyboard = [
        [subscription_button, cancel_button]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = build_start_message(subscribed, authorized=True)

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
