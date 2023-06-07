from discord.ext.commands import Cog, Bot, Context
from discord.ext import commands


# todo: PingPongCog
class PingPong(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command(description='Simple command that responds with Pong!')
    async def ping(self, ctx: Context) -> None:
        await ctx.send(f'Pong! Bot ping is {ctx.bot.latency}')


async def setup(bot: Bot) -> None:
    await bot.add_cog(PingPong(bot))
