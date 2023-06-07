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
class Emoji(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_group(aliases=('emote', 'reaction'))
    async def emoji(self, ctx: Context) -> None:
        pass

    @emoji.command(aliases=('info',), description='Get info about used emojis')
    @app_commands.describe(emoji=':emoji: or emoji_name or EMOJI_ID or https://emoji_url')
    async def get(
            self, ctx: Context,
            emoji: CustomEmojiConverter = commands.parameter(description=':emoji: or emoji_name or emoji_ID or emoji_url')) -> None:
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

    @emoji.command(description='Puts a reaction to the specified message so that after, the author clicks on it')
    @app_commands.describe(
        emoji=':emoji: or emoji_name or EMOJI_ID or https://emoji_url',
        message_id='ID of the message to which you need to put a reaction')
    async def send(
            self, ctx: Context,
            emoji: CustomEmojiConverter = commands.parameter(description=':emoji: or emoji_name or EMOJI_ID or https://emoji_url'),
            message_id: str = commands.parameter(description='ID of the message to which you need to put a reaction', default=None)):

        def check(reaction: Reaction, user: Member):
            return reaction.message == message and reaction.emoji == emoji and user == ctx.author

        if not ctx.interaction:
            await ctx.message.delete()
        else:
            await ctx.defer(ephemeral=True)

        if emoji is None:
            return await ctx.send(r'Sorry, could not find the specified emoji. ¯\_(ツ)_/¯', delete_after=10.0)
        if message_id and not message_id.isdigit():
            return await ctx.send_help('emoji send')

        message_id = message_id or getattr(ctx.message.reference, 'message_id', None)
        try:
            message = None
            message_id = int(message_id)
        except ValueError:
            try:
                message: Message = await anext(ctx.channel.history(limit=1, oldest_first=False))
            except StopAsyncIteration:  ...
        else:
            try:
                message: Message = await ctx.fetch_message(message_id)
            except NotFound:  ...
        finally:
            if message is None:
                return await ctx.reply(r'Did not find the specified message. ¯\_(ツ)_/¯', delete_after=10.0)

        try:
            await message.add_reaction(emoji)
        except (NotFound, TypeError):
            return await ctx.send(r'Sorry, I couldn\'t add emoji to the message. ¯\_(ツ)_/¯')

        if ctx.interaction:
            await ctx.reply('Emoji successfully added, please click on it')

        try:
            await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:  ...
        finally:
            await message.remove_reaction(emoji, self.bot.user)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Emoji(bot))
