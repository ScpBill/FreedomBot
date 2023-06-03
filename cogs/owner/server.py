from discord.ext.commands import Cog, Bot, Context
from discord import Message, ButtonStyle, Interaction
from discord.ui import View, Button
from discord.ext import commands
from discord import app_commands, ui

from spec.config import Config

import subprocess
import typing
import time
import sys
import os


class Console:
    def __init__(self, *, args: str):
        self._pattern_title = '**Executing the command `{args}`:**'
        self._pattern_footer = '**Return code: `{code}`**'
        self.content: str = ''
        self.args: str | None = args
        self.result_code: int | None = None
        self.current_page: int | None = 1
        self._last_call_time: float | None = None

    @staticmethod
    def _execute_with_generator(shell: str) -> typing.Generator:
        popen = subprocess.Popen(shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
                                 shell=True)

        for stdout_line in iter(popen.stdout.readline, ''):
            yield stdout_line, None
        for stderr_line in iter(popen.stderr.readline, ''):
            yield stderr_line, None

        popen.stdout.close()
        popen.stderr.close()
        yield '', popen.wait()

    async def send_execution(self, *, msg: Message = None) -> None:
        for line, code in self._execute_with_generator(self.args):
            string_with_new_line = line.replace('``', "`​`")

            self.content += string_with_new_line
            self.result_code = code

            if msg is not None:
                await self._edit_message_include_cooldown(
                    message=msg, content=self.full_message, necessarily=self.result_code is not None,
                    view=PagesView(self))

    @property
    def title(self) -> str:
        return f'{self._pattern_title.format(args=self.args)}\n' if self.args is not None else ''

    @property
    def footer(self) -> str:
        return f'\n{self._pattern_footer.format(code=self.result_code)}' if self.result_code is not None else ''

    @property
    def accept_length(self) -> int:
        return 2000 - len(self.title) - len(self.footer) - 8  # other chars

    @property
    def segments_text(self) -> list[str]:
        segments = ['']
        for line in self.content.split('\n'):
            if len(segments[-1]) + len(line) < self.accept_length:
                segments[-1] += '\n%s' % line
            else:
                if not segments[-1]:
                    segments.pop()
                for s in range(0, len(line), self.accept_length):
                    segments.append(line[s:s + self.accept_length])
        return segments

    @property
    def full_message(self) -> str:
        if self.small_message:
            return self.title + self.small_message + self.footer
        return f'{self.title[:-1]}{self.footer}'

    @property
    def small_message(self) -> str:
        if self.cut_content:
            return f'```\n{self.cut_content}\n```'
        return ''

    @property
    def cut_content(self) -> str:
        if self.content:
            return self.segments_text[self.current_page - 1]
        return ''

    async def _edit_message_include_cooldown(
            self, message: Message, *, content: str, necessarily: bool = False, view: View = None) -> Message:
        cooldown = 0.5

        if (self._last_call_time is None) or (time.time() - self._last_call_time > cooldown) or necessarily:
            self._last_call_time = time.time()

            return await message.edit(content=content, view=view)
        return message


class PagesView(View):
    children: list[Button]

    def __init__(self, console: Console):
        super().__init__()
        self.console = console
        self.check_state_buttons()

    def check_state_buttons(self):
        if self.console.current_page == 1:
            self.children[0].disabled = True
        else:
            self.children[0].disabled = False

        self.children[1].label = '{} / {}'.format(
            self.console.current_page, len(self.console.segments_text))

        if self.console.current_page == len(self.console.segments_text):
            self.children[2].disabled = True
        else:
            self.children[2].disabled = False

    @ui.button(label='', disabled=True, style=ButtonStyle.gray, emoji='⬅', custom_id='back')
    async def back_page(self, interaction: Interaction, button: Button):

        if self.console.current_page > 1:  # current_page is not first
            self.console.current_page -= 1

        self.check_state_buttons()
        await interaction.response.edit_message(content=self.console.full_message, view=self)

    @ui.button(label='1 / 1', disabled=True, style=ButtonStyle.gray, custom_id='count')
    async def count_page(self, interaction: Interaction, button: Button): pass

    @ui.button(label='', disabled=False, style=ButtonStyle.gray, emoji='➡', custom_id='next')
    async def next_page(self, interaction: Interaction, button: Button):

        # current_page is not last
        if self.console.current_page < len(self.console.segments_text):
            self.console.current_page += 1

        self.check_state_buttons()
        await interaction.response.edit_message(content=self.console.full_message, view=self)


class ServerManagement(Cog, name='Server Management', description='Managing the bot\'s command tree',
                       command_attrs=dict(hidden=True, guild_ids=[Config.ID_GUILD])):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command(
        name='update', description='Updating project files using the GitHub repository',
        help='Commands, running applications or packages', usage='update')
    @commands.is_owner()
    async def _update(self, ctx: Context) -> None:
        await ctx.defer()
        answer: Message = await ctx.reply('**Executing update commands:**', mention_author=False)

        console = Console(args='git reset --hard')
        await console.send_execution()
        if not console.result_code:
            answer: Message = await answer.edit(
                content=answer.content + '\n> `✅` The git *reset* command was executed successfully')
        else:
            answer: Message = await answer.edit(
                content=answer.content + '\n> `❌` The git *reset* command was executed with the code `{}`'
                                         ''.format(console.result_code))

        console = Console(args='git pull origin master')
        await console.send_execution()
        if not console.result_code:
            answer: Message = await answer.edit(
                content=answer.content + '\n> `✅` The git *pull* command was executed successfully')
        else:
            answer: Message = await answer.edit(
                content=answer.content + '\n> `❌` The git *pull* command was executed with the code `{}`'
                                         ''.format(console.result_code))

        await answer.edit(content='**The update was successful**')

    @commands.hybrid_command(
        name='console', aliases=['cmd', 'shell'], description='Shell Command Management',
        help='Be extremely careful with specifying arguments', usage='<console|cmd|shell> <args>')
    @commands.is_owner()
    @app_commands.describe(args='Commands, running applications or packages')
    async def _console(self, ctx: Context, *, args: str) -> None:
        await ctx.defer()

        console = Console(args=args)
        replied_msg: Message = await ctx.reply(console.full_message, mention_author=False)
        await console.send_execution(msg=replied_msg)

    @commands.hybrid_command(name='restart', description='Restart the bot', help='Restart the bot', usage='<restart>')
    @commands.is_owner()
    async def _restart(self, ctx: Context) -> None:
        await ctx.defer()

        await ctx.reply('OK, I\'m starting to restart...', mention_author=False)
        os.execv(sys.executable, ['python'] + sys.argv)


async def setup(bot: Bot) -> None:
    await bot.add_cog(ServerManagement(bot))
