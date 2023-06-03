from discord.ext.commands import Cog, Bot, Context
from discord.app_commands import Choice
from discord.ext import commands
from discord import app_commands, Member, Embed, Colour

from spec.config import Config

import os


class Test(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
    
    @commands.hybrid_command()
    async def testmember(self, ctx: Context):
        await ctx.send(f'{ctx.author.name=}'
                       f'\n{ctx.author.nick=}'
                       f'\n{ctx.author.display_name=}')


async def setup(bot: Bot) -> None:
    await bot.add_cog(Test(bot))
