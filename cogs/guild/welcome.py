from discord.ext.commands import Cog, Bot, Context
from discord.app_commands import Choice
from discord.ext import commands
from discord import app_commands, Member, Embed, Colour

from spec.config import Config

import os


class Welcome(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        if member.guild.id == 948239228989493338:
            message = Embed(
                title='Добро пожаловать на «Freedom»!',
                description=
                    'Вы попали на интереснейший сервер, где каждый может найти для себя увлекательное дело.'
                    '\n- Ознакомиться с проектом можно в <#1113060299826802800>.'
                    '\n- Не забудьте прочитать наши правила: <#1113060541771038800>.',
                timestamp=member.joined_at,
                colour=member.accent_colour if member.accent_colour else Colour(0x2d4db4)
            )
            message.set_author(name=f'{member.name}#{member.discriminator}')
            message.set_footer(text=f'User ID: {member.id}', icon_url=member.guild.icon)
            message.set_thumbnail(url=getattr(member.avatar, 'url', None))

            await member.guild.get_channel(1113059101539315722).send(
                content=f'**Здравствуй {member.mention}!**',
                embed=message
            )


async def setup(bot: Bot) -> None:
    await bot.add_cog(Welcome(bot))
