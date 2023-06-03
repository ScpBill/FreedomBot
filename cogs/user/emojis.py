from discord.ext.commands import Cog, Bot, Context, Converter
from discord import Embed, Emoji, Reaction, Member, Message, NotFound
from discord.ext import commands
from discord import app_commands
from discord import utils

from emoji import is_emoji, emojize, demojize
import asyncio
import re


class StandardEmoji:
    def __init__(self, icon, name):
        self.icon = icon
        self.name = name


class CustomEmojiConverter(Converter):
    async def convert(self, ctx: Context, argument: str):
        if utils.get(ctx.bot.emojis, name=argument):  # Emoji
            emoji = utils.get(ctx.bot.emojis, name=argument)
        elif argument.isnumeric():  # ID
            emoji = ctx.bot.get_emoji(int(argument))
        elif re.fullmatch(r'(:\w+:)|(<\w*:\w+:\w+>)', argument):  # :emoji: | <*a:emoji:id>
            emoji = utils.get(ctx.bot.emojis, name=argument.split(':')[1])
        elif isinstance(argument, str) and re.match(r'^(?:http|ftp)s?://', argument):
            emoji = utils.get(ctx.bot.emojis, url=argument)
        elif isinstance(argument, str):  # Standard
            data = emojize(argument, language='alias', variant='emoji_type')
            emoji = StandardEmoji(data, demojize(data, language='alias', delimiters=('', ''))) if \
                is_emoji(data) else None
        else:
            emoji = None
        return emoji


# todo: send_reaction()
class EmojiCogs(Cog, name='Manager for emojis'):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command(name='emoji', aliases=['emote'], description='Get info about used emojis',
                             help='Get info', usage='emoji <:emoji:|emoji_name|emoji_id>')
    @app_commands.describe(emoji=':emoji: or emoji_name or emoji_ID or emoji_url')
    async def emoji(self, ctx: Context, emoji: CustomEmojiConverter) -> None:
        await ctx.defer()

        if emoji is None:
            await ctx.reply(r'Sorry, could not find the specified emoji. ¯\_(ツ)_/¯', mention_author=False)
        elif isinstance(emoji, Emoji):
            embed = Embed(
                title='Info about «%s» emoji' % emoji,
                description=f'*It is custom emoji*'
                            f'\nAnimated: {"`%s`" % emoji.animated}'
                            f'\nName: {"`%s`" % emoji.name}'
                            f'\nID: {"`%s`" % emoji.id}'
                            f'\nFull name: {"`%s`" % emoji.__str__()}'
                            f'\nGuild: {"`%s`" % getattr(emoji.guild, "name", "None")}'
                            f'\nCreated at: {"`%s`" % emoji.created_at.strftime("%d %B %Y %H:%M:%S %Z")}')
            embed.set_image(url=emoji.url)
            await ctx.reply(embed=embed, mention_author=False)
        elif isinstance(emoji, StandardEmoji):
            embed = Embed(
                title='Info about «%s» emoji' % emoji.icon,
                description=f'*It is standard emoji*'
                            f'\nIcon: {"`%s`" % emoji.icon}'
                            f'\nName: {"`%s`" % emoji.name}')
            await ctx.reply(embed=embed, mention_author=False)

    @commands.hybrid_command(aliases=('reaction', 'send_emoji', 'rs'))
    async def send_reaction(self, ctx: Context,
                            emoji: str = commands.parameter(
                                description='Emoji'),
                            id_message: str = commands.parameter(description='ID message', default=None)):
        """Puts a reaction to the specified message so that after, the author clicks on it"""
        get_emoji = getattr(self.bot.get_cog('ManageChat'), 'get_emoji')

        def check(this_reaction: Reaction, this_user: Member):
            return this_reaction.message == current_message and this_reaction.emoji == emoji and this_user == ctx.author

        # Waiting message
        await ctx.defer(ephemeral=True)
        if not ctx.interaction:
            await ctx.message.delete()

        # Getting emoji
        emoji = await get_emoji(self.bot, emoji)
        if emoji is None:
            await ctx.send(r'Sorry, could not find the specified emoji. ¯\_(ツ)_/¯', ephemeral=True)
            return

        # Get a current message id
        if id_message is None and ctx.message.reference:
            id_message = ctx.message.reference.message_id

        # And get a current message
        try:
            assert id_message is not None
            current_message: Message = await ctx.fetch_message(int(id_message))
        except AssertionError:
            current_message: Message = [msg async for msg in ctx.channel.history(limit=1)].pop(0)
        except NotFound:
            await ctx.reply('Did not find the specified message', ephemeral=True, delete_after=10.0)
            return

        # Add reaction to message
        try:
            await current_message.add_reaction(emoji)
        except (NotFound, TypeError):
            await ctx.send(r'Sorry, could not find the specified emoji. ¯\_(ツ)_/¯', ephemeral=True)
            return

        if ctx.interaction:
            await ctx.reply('Emoji successfully added', ephemeral=True)

        # Wait author click on reaction
        try:
            await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            pass

        # Remove my self reaction
        await current_message.remove_reaction(emoji, self.bot.user)


async def setup(bot: Bot) -> None:
    await bot.add_cog(EmojiCogs(bot))
