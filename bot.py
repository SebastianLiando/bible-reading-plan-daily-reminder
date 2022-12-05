from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from config.env import TOKEN, USE_WEBHOOK
from telegram_bot.const import WEBHOOK_SETTINGS
from telegram_bot.bot_manager import BotManager
from telegram_bot.handler import commands, on_message, on_subscription_change


def create_command_handlers(item) -> CommandHandler:
    command, callback = item
    return CommandHandler(command, callback)


def main():
    bot_manager = BotManager(TOKEN)

    # Add bot commands
    command_callbacks = list(map(create_command_handlers, commands.items()))
    bot_manager.add_handlers(*command_callbacks)

    # Add listener to inline keyboards
    keyboard_handler = CallbackQueryHandler(on_subscription_change)
    bot_manager.add_handlers(keyboard_handler)

    # Text messages to respond to, this is mainly for telegram channels
    texts_to_respond = list(
        map(lambda command: f'/{command}', commands.keys())
    )
    message_handler = MessageHandler(
        Filters.text(texts_to_respond),
        on_message
    )
    bot_manager.add_handlers(message_handler)

    print('Starting bot')
    bot_manager.start_bot(USE_WEBHOOK, WEBHOOK_SETTINGS)


if __name__ == '__main__':
    main()
