from discord.ext.commands import Cog, Bot, Context
from discord.app_commands import Choice
from discord.ext import commands
from discord import app_commands

from spec.config import Config

import os


class Loader(Cog, name='Loader', description='Managing extensions and loading cogs into them',
             command_attrs=dict(hidden=True, guild_ids=[Config.ID_GUILD])):
    successful = '\n> `✅` Extension `{cog}` is successful {do}ed'
    unsuccessful = '\n> `❌` Extension `{cog}` is not {do}ed due to `{exc.__class__.__name__}`: ||`{exc}`||'
    answer = '**Results of {} extensions:**'

    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    def get_extensions(folder: str = 'all', *, cog_name: str = None) -> list[str]:
        """
        Getting paths of all extensions in project

        >>> Loader.get_extensions()
        ['cogs.admin.loader', ...]
        """
        if cog_name is not None:
            return [f'cogs.{cog_name}']

        extensions = []
        for _dir_name in os.listdir('./cogs'):
            if not (os.path.isdir(_dir := os.path.join('./cogs', _dir_name))) or (
                    folder not in ('all', _dir_name)):
                continue
            for _ext_name in os.listdir(_dir):
                if not os.path.isfile(os.path.join(_dir, _ext_name)) or not _ext_name.endswith('.py'):
                    continue
                _ext_name = _ext_name[:-3]
                extensions.append(f'cogs.{_dir_name}.{_ext_name}')

        return extensions

    @commands.hybrid_group(
        name='ext', aliases=['extensions'], description='{} the extension with the name or all',
        help='{} the extension with the name or all', usage='<ext|extensions> {} <dir.name>|<dir>|all')
    async def _ext_group(self, ctx: Context) -> None:  ...

    @_ext_group.command(
        name='load', description=_ext_group.description.format('Load'), help=_ext_group.help.format('Load'),
        usage=_ext_group.usage.format('load'))
    @app_commands.describe(extensions='Choose file from the list')
    @commands.is_owner()
    async def _ext_load(self, ctx: Context, *, extensions: str) -> None:
        await ctx.defer()
        answer = await ctx.reply(self.answer.format('load'), mention_author=False)

        for path in self.get_extensions(extensions, cog_name=extensions if '.' in extensions else None):
            # Remove 'bot.cogs.' from the path name
            cog = '.'.join(path.split('.')[1:])
            try:
                await self.bot.load_extension(path)
            except Exception as exc:
                answer = await answer.edit(
                    content=answer.content + self.unsuccessful.format(cog=cog, exc=exc, do='load'))
            else:
                answer = await answer.edit(
                    content=answer.content + self.successful.format(cog=cog, do='load'))

        await answer.edit(content=answer.content + '\n**The operation has ended**')

    @_ext_group.command(
        name='unload', description=_ext_group.description.format('Unload'), help=_ext_group.help.format('Unload'),
        usage=_ext_group.usage.format('unload'))
    @app_commands.describe(extensions='Choose file from the list')
    @commands.is_owner()
    async def _ext_unload(self, ctx: Context, *, extensions: str) -> None:
        await ctx.defer()
        answer = await ctx.reply(self.answer.format('unload'), mention_author=False)

        for path in self.get_extensions(extensions, cog_name=extensions if '.' in extensions else None):
            # Remove 'bot.cogs.' from the path name
            cog = '.'.join(path.split('.')[1:])
            try:
                await self.bot.unload_extension(path)
            except Exception as exc:
                answer = await answer.edit(
                    content=answer.content + self.unsuccessful.format(cog=cog, exc=exc, do='unload'))
            else:
                answer = await answer.edit(
                    content=answer.content + self.successful.format(cog=cog, do='unload'))

        await answer.edit(content=answer.content + '\n**The operation has ended**')

    @_ext_group.command(
        name='reload', description=_ext_group.description.format('Reload'), help=_ext_group.help.format('Reload'),
        usage=_ext_group.usage.format('reload'))
    @app_commands.describe(extensions='Choose file from the list')
    @commands.is_owner()
    async def _ext_reload(self, ctx: Context, *, extensions: str) -> None:
        await ctx.defer()
        answer = await ctx.reply(self.answer.format('reload'), mention_author=False)

        for path in self.get_extensions(extensions, cog_name=extensions if '.' in extensions else None):
            # Remove 'bot.cogs.' from the path name
            cog = '.'.join(path.split('.')[1:])
            try:
                await self.bot.reload_extension(path)
            except Exception as exc:
                answer = await answer.edit(
                    content=answer.content + self.unsuccessful.format(cog=cog, exc=exc, do='reload'))
            else:
                answer = await answer.edit(
                    content=answer.content + self.successful.format(cog=cog, do='reload'))

        await answer.edit(content=answer.content + '\n**The operation has ended**')

    @_ext_load.autocomplete('extensions')
    @_ext_unload.autocomplete('extensions')
    @_ext_reload.autocomplete('extensions')
    async def _ext_autocomplete(self, ctx: Context, current: str):
        bot_extensions = self.bot.extensions
        filtered_extensions, filtered_directories, completed = [], [], []

        def check_all():
            if ctx.command.name == 'load':
                return not set(self.get_extensions()).issubset(bot_extensions)
            if ctx.command.name in ('unload', 'reload'):
                # Always true
                return set(self.get_extensions()).intersection(bot_extensions)

        def check_dir(folder):
            if ctx.command.name == 'load':
                return not set(self.get_extensions(folder)).issubset(bot_extensions)
            if ctx.command.name in ('unload', 'reload'):
                return set(self.get_extensions(folder)).intersection(bot_extensions)

        def check_ext(ext):
            if ctx.command.name == 'load':
                return ext not in bot_extensions
            if ctx.command.name in ('unload', 'reload'):
                return ext in bot_extensions

        # Filtering lists
        if current.lower() in '💻 all' and check_all():
            completed.append('all')

        for _folder in os.listdir('./cogs'):
            if not check_dir(_folder):
                continue
            if current.lower() in '📁 ' + _folder:
                filtered_directories.append(_folder)

        for _extension in self.get_extensions():
            if not check_ext(_extension):
                continue
            if current.lower() in '🔩 ' + (_small_ext := '.'.join(_extension.split('.')[1:])):
                filtered_extensions.append(_small_ext)

        completed.extend(filtered_directories)
        completed.extend(filtered_extensions)

        return [Choice(name=f'💻 {option}', value=option) if option == 'all' else
                Choice(name=f'📁 {option}', value=option) if '.' not in option else
                Choice(name=f'🔩 {option}', value=option) for option in completed]


async def setup(bot: Bot) -> None:
    await bot.add_cog(Loader(bot))
