from telegram.constants import PARSEMODE_HTML
from eventbrite import get_next_jcc_sermon
from telegram_bot.const import CALLBACK_DATA_CANCEL, LABEL_CANCEL_OPERATION, build_service_reminder_message, build_subscription_change_message
from telegram import Update
from telegram.ext import CallbackContext
from telegram_bot.handler_utils import toggle_subscription, is_sender_authorized, reply_authorized, reply_unauthorized
from telegram_bot.utils import get_message_for_today
from google.cloud import firestore


def on_command_start(update: Update, _: CallbackContext):
    """Handler for the command `/start`

    Args:
        update (Update): The update.
        _ (CallbackContext): The callback context.
    """
    print(f'From: {update.effective_chat}')

    chat_id = update.effective_chat.id

    if is_sender_authorized(update.effective_chat, update.effective_user):
        reply_authorized(chat_id, update)
    else:
        reply_unauthorized(chat_id, update)


def on_command_today(update: Update, _: CallbackContext):
    """Callback when the user calls `/today` command.

    Args:
        update (Update): The update object
        _ (CallbackContext): The context object.
    """
    if is_sender_authorized(update.effective_chat, update.effective_user):
        db = firestore.Client()
        todays_content = get_message_for_today(db)

        for i in range(0, len(todays_content), 4000):
            update.effective_chat.send_message(
                text=todays_content[i:i+4000],
                parse_mode=PARSEMODE_HTML
            )


def on_command_sermon(update: Update, _: CallbackContext):
    if is_sender_authorized(update.effective_chat, update.effective_user):
        event = get_next_jcc_sermon()

        if event is None:
            message = build_service_reminder_message(None)
        else:
            message = build_service_reminder_message(event.url)

        update.effective_chat.send_message(
            message,
            parse_mode=PARSEMODE_HTML,
        )


commands = {
    'start': on_command_start,
    'today': on_command_today,
    'sermon': on_command_sermon,
}
"""Commands and the corresponding callback function."""


def on_message(update: Update, callback: CallbackContext):
    text = update.effective_message.text

    # Message must start with slash
    if text[0] == '/':
        # Drop the slash for matching to command
        text = text[1:]
    else:
        return

    # Redirect to command callbacks
    if text in commands.keys():
        handler_callback = commands[text]
        handler_callback(update, callback)


def on_subscription_change(update: Update, _: CallbackContext):
    query = update.callback_query

    # Get the data send by the inline keyboard.
    chat_id = query.data

    # If the user cancels the operation.
    if (chat_id == CALLBACK_DATA_CANCEL):
        query.edit_message_text(text=LABEL_CANCEL_OPERATION)
        return

    # Else, modify the subscription for the given chat id.
    subscribed = toggle_subscription(chat_id)

    # Notify that the user has changed the subscription
    reply = build_subscription_change_message(subscribed)
    query.edit_message_text(text=reply)
