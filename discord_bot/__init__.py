from datetime import datetime
import discord

COLOR_SUCCESS = 0x00FF00
COLOR_ERROR = 0xFF0000

CHANNEL_NAME = 'pulse-bible'


def today_date_str() -> str:
    return datetime.now().strftime('%d %b %Y')


class ReportBot(discord.Client):
    def __init__(self, success: bool, message: str, loop=None, **options):
        super().__init__(loop=loop, **options)
        self.success = success
        self.message = message

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        guild: discord.Guild
        for guild in self.guilds:
            print(f'Guild: {guild.name}({guild.id})')

            channel: discord.abc.GuildChannel
            for channel in guild.channels:
                if isinstance(channel, discord.channel.TextChannel) and channel.name == CHANNEL_NAME:
                    embed_msg = self.embed_message
                    content = None if self.success else "@everyone"

                    await channel.send(content=content, embed=embed_msg)

        await self.close()

    @property
    def embed_message(self):
        if self.success:
            return discord.Embed(
                title=f"(SUCCESS) {today_date_str()}",
                color=COLOR_SUCCESS,
                description=self.message
            )
        else:
            return discord.Embed(
                title=f"(ERROR) {today_date_str()}",
                color=COLOR_ERROR,
                description=self.message
            )
