from telegram_bot.const import CALLBACK_DATA_CANCEL, LABEL_CANCEL_OPERATION, build_subscription_change_message
from telegram import Update
from telegram.ext import CallbackContext
from telegram_bot.handler_utils import toggle_subscription, is_sender_authorized_to_modify, reply_authorized, reply_unauthorized


def on_command_start(update: Update, _: CallbackContext):
    """Handler for the command `/start`

    Args:
        update (Update): The update.
        _ (CallbackContext): The callback context.
    """
    print(f'From: {update.effective_chat}')

    chat_id = update.effective_chat.id

    if is_sender_authorized_to_modify(update.effective_chat, update.effective_user):
        reply_authorized(chat_id, update)
    else:
        reply_unauthorized(chat_id, update)


commands = {
    'start': on_command_start
}


def on_message(update: Update, callback: CallbackContext):
    text = update.effective_message.text

    # Drop the slash
    if text[0] == '/':
        text = text[1:]

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
