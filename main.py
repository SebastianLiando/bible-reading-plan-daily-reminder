import telegram
from data.subscriber_repository import SubscriptionItem
from telegram_bot.env import TOKEN
from google.cloud import firestore
from telegram_bot.utils import get_message_for_today, get_subscribers_chat_ids


def main():
    # Create the database client
    db = firestore.Client()

    # Get today's message
    telegram_message = get_message_for_today(db)

    # Get all subscribers
    subscribers = get_subscribers_chat_ids(SubscriptionItem.PULSE_BIBLE_READING_PLAN)

    # Exit if there are no subscribers
    if len(subscribers) == 0:
        print('No subscribers to send')
        return

    # Get access to the bot
    bot = telegram.Bot(token=TOKEN)

    # Send the message to all subscribers
    for chat_id in subscribers:
        # Send message every 4000 characters, this is telegram's limitation.
        for i in range(0, len(telegram_message), 4000):
            sub_message = telegram_message[i:i+4000]

            bot.send_message(
                chat_id=chat_id,
                text=sub_message,
                parse_mode=telegram.ParseMode.HTML
            )

    print(f'Successfully sent messages to {len(subscribers)} subscriber(s)')


if __name__ == "__main__":
    main()
