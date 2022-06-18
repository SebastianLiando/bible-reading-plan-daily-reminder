# Bible Reading Plan Daily Reminder

A multipurpose telegram bot for reminders on Jurong Christian Church, such as sending Bible reading plan or Sunday service registration.

![Bot preview](/assets/preview.png)

## Setup

### Environment Variables

These are the required environment variables.

| Name              | Description                                                                                                |
| ----------------- | ---------------------------------------------------------------------------------------------------------- |
| BOT_BASE_URL      | The webhook URL of the bot.                                                                                |
| BOT_TOKEN         | The token of the bot to be used.                                                                           |
| DISCORD_BOT_TOKEN | The token for the discord bot used to report status                                                        |
| BOT_WEBHOOK       | Set this to `true` if the bot should run using webhook. If set to `false`, the bot will run using polling. |

### Google Application Credentials

This project uses Firebase as the backend service. Ensure that the deployment environment has been setup for Firebase.

## Scripts

### `bot.py`

This script starts the telegram bot. The bot currently has 3 available commands. All commands are available to personal chat with the bot. However, privileged commands are only available to owners and admins for groups, supergroups, and channels.

| Command  | Privileged | Description                                                   |
| -------- | ---------- | ------------------------------------------------------------- |
| /start   | YES        | Changes the chat's subscription to the reminder.              |
| /today   | YES        | Calls the bot to send today's reading plan.                   |
| /service | YES        | Calls the bot to send the upcoming service registration link. |
| /help    | YES        | General introduction to the bot.                              |

### `main.py`

This script sends today's reading plan to every subscriber. This is the script should run in a cron job.

### (Deprecated) `service_reminder.py`

This script sends Evenbrite registration reminder to every subscriber. This is the script should run in a cron job.

### `upload_csv.py`

This script is used to upload the reading plan in CSV format to the Firestore database.

#### CSV Format

The first row is the heading: `date`, `book`, `chapter`, `start_verse`, `end_verse`.

The values for each heading is as follows.

| Heading       | Description                                                                                        | Example   |
| ------------- | -------------------------------------------------------------------------------------------------- | --------- |
| `date`        | The date of the plan in `DD-MMM-YY` format.                                                        | 25-Sep-21 |
| `book`        | The Bible book name.                                                                               | Romans    |
| `chapter`     | The chapter number.                                                                                | 1         |
| `start_verse` | The starting verse number (inclusive). If this is blank, then it defaults to 1.                    | 1         |
| `end_verse`   | The ending verse number (inclusive). If this is blank, then it defaults to the end of the chapter. | 10        |
