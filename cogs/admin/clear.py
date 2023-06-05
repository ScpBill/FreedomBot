from discord.ext.commands import Cog, Bot, Context, FlagConverter, BadArgument
from discord import Member, Message
from discord.ext import commands
from discord import app_commands

import re
import datetime


class TimePeriodConverter(FlagConverter):

    async def convert(self, ctx: Context, *, argument: str) -> datetime.datetime:
        timedelta = datetime.timedelta()
        # [1, w, 2, d, 3, h, 4, m, 5, s]
        parts: list[str] = re.findall(r'\D+|\d+', argument.replace(' ', ''))
        for num, form in zip(parts[::2], parts[1::2]):
            if not num.isdigit() or form.isdigit():
                raise BadArgument()
            if form in ('w', 'weak', 'weaks', 'н', 'неделя', 'недели', 'недель'):
                timedelta += datetime.timedelta(days=7*num)
            elif form in ('d', 'day', 'days', 'д', 'день', 'дня', 'дней', 'сутки', 'суток'):
                timedelta += datetime.timedelta(days=num)
            elif form in ('h', 'hour', 'hours', 'ч', 'час', 'часа', 'часов'):
                timedelta += datetime.timedelta(hours=num)
            elif form in ('m', 'minute', 'minutes', 'м', 'минута', 'минуты', 'минут'):
                timedelta += datetime.timedelta(minutes=num)
            elif form in ('s', 'second', 'seconds', 'с', 'секунда', 'секунды', 'секунд'):
                timedelta += datetime.timedelta(seconds=num)
            else:
                raise BadArgument()
        return ctx.message.created_at - timedelta


class Clear(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
    
    @commands.hybrid_command(name='clear', aliases=['очистить', 'purge'], description='Очищает сообщения в данном канале')
    @app_commands.describe(
        count='Число сообщений, нуждающихся в очистке',
        members='Пользователи, чьи сообщения будут очищены')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: Context, count: int = None, *, time: TimePeriodConverter = None, members: commands.Greedy[Member]):
        answer = await ctx.reply('<a:Loading:749672972079333497> In the process of cleaning...', allowed_mentions=False)

        def check_on_author(message: Message) -> bool:
            return message.author in members

        await ctx.channel.purge(
            limit=count,
            check=check_on_author,
            after=time,
            before=ctx.message.created_at,
            reason='the command to clear the chat'
        )

        await answer.edit(content='✅ Cleaning was successful', delete_after=5.0)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Clear(bot))
