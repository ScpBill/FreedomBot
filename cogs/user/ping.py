from discord.ext.commands import Cog, Bot, Context
from discord.ext import commands


# todo: PingPongCog
class PingPongCog(Cog, name='Ping Pong'):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command()
    async def ping(self, ctx: Context) -> None:
        """Simple command that responds with Pong!"""
        await ctx.send('Pong!')


async def setup(bot: Bot) -> None:
    await bot.add_cog(PingPongCog(bot))
