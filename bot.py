from discord import Intents
from discord.ext import commands

from spec.env import Env
from spec.config import Config


def start_bot():
    bot = RinderpestBot(Intents.all())
    bot.run(Env.TOKEN)


class RinderpestBot(commands.Bot):
    def __init__(self, intents: Intents, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or(Config.CMD_PREFIX), intents=intents,
                         case_insensitive=True, strip_after_prefix=True, **kwargs)

    async def setup_hook(self):
        for cog in Config.STANDARD_EXTENSIONS:
            path = f'bot.cogs.{cog}'
            try:
                await self.load_extension(path)
            except Exception as exc:
                print(f'[-] Could not load extension {cog} due to {exc.__class__.__name__}: {exc}')
            else:
                print(f'[+] The {cog} extension has been successfully installed')

    async def on_ready(self):
        print(f'[**] Logged on as "{self.user}" (ID: {self.user.id})')
