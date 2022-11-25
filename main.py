import telegram
from data import db
from data.subscriber_repository import SubscriptionItem
from config.env import TOKEN
from google.cloud import firestore
from telegram_bot.message import split_html_message
from telegram_bot.utils import get_message_for_today, get_subscribers_chat_ids
from discord_bot import ReportBot, DISCORD_BOT_TOKEN


def report_to_discord(success: bool, message: str):
    bot = ReportBot(success=success, message=message)
    bot.run(DISCORD_BOT_TOKEN)


def main():
    # Get today's message
    telegram_message = get_message_for_today(db)

    if telegram_message is None:
        print('No reading task for today.')
        report_to_discord(True, 'No reading task.')
        return

    # Get all subscribers
    subscribers = get_subscribers_chat_ids(
        SubscriptionItem.PULSE_BIBLE_READING_PLAN)

    # Exit if there are no subscribers
    if len(subscribers) == 0:
        print('No subscribers to send')
        return

    # Get access to the bot
    bot = telegram.Bot(token=TOKEN)

    # Send the message to all subscribers
    message_parts = split_html_message(telegram_message)
    try:
        for chat_id in subscribers:
            for part in message_parts:
                bot.send_message(
                    chat_id=chat_id,
                    text=part,
                    parse_mode=telegram.ParseMode.HTML
                )

        print(
            f'Successfully sent messages to {len(subscribers)} subscriber(s)')
        report_to_discord(True, "Reading task successfully sent.")
    except Exception as e:
        report_to_discord(False, f"Error in sending reading task: {e}")


if __name__ == "__main__":
    main()
