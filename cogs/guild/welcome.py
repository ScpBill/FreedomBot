from discord.ext.commands import Cog, Bot, Context
from discord.app_commands import Choice
from discord.ext import commands
from discord import app_commands, Member, Embed

from spec.config import Config

import os


class Welcome(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_member_join(member: Member) -> None:
        if member.guild.id == 948239228989493338:
            message = Embed(
                title='Добро пожаловать на «Freedom»!',
                description=
                    'Вы попали на интереснейший сервер, где каждый может найти для себя увлекательное дело.'
                    '\n- Ознакомиться с проектом можно в <#1113060299826802800>.'
                    '\n- Не забудьте прочитать наши правила: <#1113060541771038800>.',
                timestamp=member.joined_at,
                colour=member.accent_colour
            )
            message.set_author(name=member.name)
            message.set_footer(text=f'User ID: {member.id}', icon_url=member.guild.icon)

            await member.guild.get_channel(1113059101539315722).send(
                content=f'**Здравствуй {member.mention}!**',
                embed=message
            )


def setup(bot: Bot) -> None:
    bot.add_cog(Welcome(bot))
