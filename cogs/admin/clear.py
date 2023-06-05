from discord.ext.commands import Cog, Bot, Context, FlagConverter, BadArgument, Converter, MissingRequiredArgument
from discord import Member, Message
from discord.ext import commands
from discord import app_commands

import re
import datetime


class TimePeriodConverter(Converter):

    async def convert(self, ctx: Context, argument: str) -> datetime.datetime:
        timedelta = datetime.timedelta()
        # [1, w, 2, d, 3, h, 4, m, 5, s]
        parts: list[str] = re.findall(r'\D+|\d+', argument.replace(' ', ''))
        for num, form in zip(parts[::2], parts[1::2]):
            if not num.isdigit() or form.isdigit():
                raise BadArgument()
            if form in ('w', 'weak', 'weaks', 'н', 'неделя', 'недели', 'недель'):
                timedelta += datetime.timedelta(days=7*int(num))
            elif form in ('d', 'day', 'days', 'д', 'день', 'дня', 'дней', 'сутки', 'суток'):
                timedelta += datetime.timedelta(days=int(num))
            elif form in ('h', 'hour', 'hours', 'ч', 'час', 'часа', 'часов'):
                timedelta += datetime.timedelta(hours=int(num))
            elif form in ('m', 'minute', 'minutes', 'м', 'минута', 'минуты', 'минут'):
                timedelta += datetime.timedelta(minutes=int(num))
            elif form in ('s', 'second', 'seconds', 'с', 'секунда', 'секунды', 'секунд'):
                timedelta += datetime.timedelta(seconds=int(num))
            else:
                raise BadArgument()
        return ctx.message.created_at - timedelta


class ClearConverter(FlagConverter):
    count: int = None
    time: TimePeriodConverter = commands.flag(name='time', default=None)
    members: commands.Greedy[Member] = commands.flag(name='member', default=[])
    
class Clear(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command(name='clear', aliases=['очистить', 'purge'], description='Очищает сообщения в данном канале',
                             usage='clear <count|time>|<count&time> *[members]')
    @app_commands.describe(
        count='Число сообщений, нуждающихся в очистке',
        time='Период времени, за который были созданы сообщения',
        members='Пользователи, чьи сообщения будут очищены')
    @commands.has_permissions(manage_messages=True)
    async def clear(self,
                    ctx: Context,
                    count: int = None, *,
                    time: TimePeriodConverter = commands.flag(name='time', default=None),
                    members: commands.Greedy[Member] = commands.flag(name='member', default=[])):
        await ctx.defer()

        time = None if isinstance(time, commands.Flag) else time
        members = [] if isinstance(members, commands.Flag) else members
        if count is None and time is None:
            return await ctx.send_help('clear')

        answer = await ctx.reply(f'⏱️ In the process of cleaning...', allowed_mentions=False)

        def check_on_author(message: Message) -> bool:
            return message.author in members if members else True

        await ctx.channel.purge(
            limit=count,
            check=check_on_author,
            after=time if isinstance(time, datetime.datetime) else None,
            before=ctx.message.created_at,
            reason='the command to clear the chat'
        )

        await answer.edit(content='✅ Cleaning was successful!', delete_after=5.0)
    
    @clear.error
    async def clear_error(self, ctx: Context, error):
        if isinstance(error, AssertionError) or isinstance(error, MissingRequiredArgument) or isinstance(error, BadArgument):
            await ctx.send_help('clear')


async def setup(bot: Bot) -> None:
    await bot.add_cog(Clear(bot))
