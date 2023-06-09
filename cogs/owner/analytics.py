from discord.ext.commands import Cog, Bot, Context
from discord.app_commands import Choice
from discord.ext import commands
from discord import app_commands, Member, Embed, Colour

from spec.config import Config

import os


class Analytics(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.is_owner()
    async def list_guilds(self, ctx: Context) -> None:
        await ctx.defer(ephemeral=True)
        guilds = []

        for guild in self.bot.guilds:
            invite = await guild.text_channels[0].create_invite(max_uses=1, temporary=True, max_age=600)
            guilds.append(f'- [{guild.name}]({invite})')
        embed = Embed(
            title='List of guilds with me',
            description='All invitation links are valid for 10 minutes and once.\n' +
            '\n'.join(guilds)
        )
        
        await ctx.reply(embed=embed, ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Analytics(bot))
