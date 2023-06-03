from discord.ext.commands import Cog, Bot, Context
from discord.app_commands import AppCommand
from discord.ext import commands
from discord import Object

from spec.config import Config


class CommandsManagement(Cog, name='Commands Management', description='Managing the bot\'s command tree',
                         command_attrs=dict(hidden=True, guild_ids=[Config.ID_GUILD])):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.guild = Object(id=Config.ID_GUILD)

    @commands.hybrid_command(
        name='sync', aliases=['synchronization'], description='Synchronize the bot\'s commands with the command tree',
        help='', usage='<sync|synchronization>')
    @commands.is_owner()
    async def _sync(self, ctx: Context) -> None:
        await ctx.defer()

        self.bot.tree.copy_global_to(guild=self.guild)
        success_commands: list[AppCommand] = await self.bot.tree.sync(guild=self.guild)

        msg = '**Successfully synchronized commands:**\n%s' % ' '.join(
            [command.mention for command in success_commands])
        await ctx.reply(msg, mention_author=False)


async def setup(bot: Bot) -> None:
    await bot.add_cog(CommandsManagement(bot))
