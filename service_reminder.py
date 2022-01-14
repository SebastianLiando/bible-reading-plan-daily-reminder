import telegram
from data.subscriber_repository import SubscriptionItem
from eventbrite import get_next_jcc_sermon
from telegram_bot.env import TOKEN
from telegram_bot.const import build_service_reminder_message
from telegram_bot.utils import get_subscribers_chat_ids


def main():
    # Get service message
    event = get_next_jcc_sermon()

    if event is None:
        message = build_service_reminder_message(None)
    else:
        message = build_service_reminder_message(event.url)

    # Get all subscribers
    subscribers = get_subscribers_chat_ids(SubscriptionItem.SERVICE_REMINDER)

    # Exit if there are no subscribers
    if len(subscribers) == 0:
        print('No subscribers to send')
        return

    # Get access to the bot
    bot = telegram.Bot(token=TOKEN)

    # Send the message to all subscribers
    for chat_id in subscribers:
        bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=telegram.ParseMode.HTML
        )

    print(f'Successfully sent messages to {len(subscribers)} subscriber(s)')


if __name__ == "__main__":
    main()
