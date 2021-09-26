import os

# Telegram bot token
TOKEN = os.environ['BOT_TOKEN']

# Webhook port number
PORT = os.environ.get('PORT', 8443)

# Whether to use webhook
USE_WEBHOOK = bool(os.environ.get('BOT_WEBHOOK', 'False'))

# Webhook URL
BASE_URL = os.environ.get('BOT_BASE_URL', '')
