from dataclasses import dataclass
from telegram.ext import Updater


@dataclass
class BotWebhookSettings:
    """ The bot's webhook connection configuration data. """

    listen_ip: str
    """ The IP address to listen to. """

    port: int
    """ The port number to use. 
    See https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks.
    """

    base_url: str
    """The webhook base URL. For heroku, use the app URL (https://<app-name>.herokuapp.com/)."""


class BotManager:
    def __init__(self, token: str) -> None:
        self.token = token
        self.updater = Updater(token=token, use_context=True)

    def add_handlers(self, *handlers):
        """ Add handlers to the bot."""

        for handler in handlers:
            self.updater.dispatcher.add_handler(handler)

    def start_bot(self, use_webhook: bool = False, webhook: BotWebhookSettings = None):
        """ Spin up the bot.

        Args:
            use_webhook (bool, optional): Wether to use webhook. Defaults to False, which is polling.
            webhook (BotWebhookSettings, optional): The webhook settings. Defaults to None. This should be
                provided if `use_webhook` is `True`.
        """

        if not use_webhook:
            # Polling
            self.updater.start_polling()
            self.updater.idle()
        else:
            # Webhook
            self.updater.start_webhook(
                listen=webhook.listen_ip,
                port=webhook.port,
                url_path=self.token,
                webhook_url=f'{webhook.base_url}' + self.token
            )
