import os
import json
from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()

# Telegram bot token
TOKEN = os.environ['BOT_TOKEN']

# Webhook port number
PORT = os.environ.get('BOT_PORT', 8443)

# Whether to use webhook
USE_WEBHOOK = bool(os.environ.get('BOT_WEBHOOK', False))

# Webhook URL
BASE_URL = os.environ.get('BOT_BASE_URL', '')

# URL for the google sheet that contains the reading tasks schedule
GOOGLE_SHEET_TASK_URL = os.environ.get(
    'GOOGLE_SHEET_TASK_URL', 'https://docs.google.com/spreadsheets/d/1FgrgQr8JmvDi98fuVFn41scB42nGUv2a96DRWYj_4M4')

# The headers for the table of the google sheet containing the reading tasks schedule
GOOGLE_SHEET_TASK_HEADERS = os.environ.get('GOOGLE_SHEET_TASK_HEADERS')
if GOOGLE_SHEET_TASK_HEADERS is None:
    GOOGLE_SHEET_TASK_HEADERS = ['Dates', 'Week', 'Day 1', 'Day 2',
                                 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Remarks']
else:
    GOOGLE_SHEET_TASK_HEADERS = GOOGLE_SHEET_TASK_HEADERS.split(",")

# Firebase admin SDK credentials
_CREDENTIALS_JSON = json.loads(
    os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'])
CREDENTIALS = service_account.Credentials.from_service_account_info(
    _CREDENTIALS_JSON)

# ----------- Discord Reporting
CHANNEL_NAME = os.environ.get('DISCORD_CHANNEL', 'pulse-bible')
DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
