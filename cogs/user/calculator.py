from discord.ext.commands import Cog, Bot, Context
from discord import Embed
from discord.ext import commands
from discord import app_commands

import sympy
import sys


# todo: CalculatorCog
class Calculator(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.hybrid_command(aliases=('calc', 'math'), description='Calculating a mathematical expression')
    @app_commands.describe(expression='String with the expression')
    async def calculator(
            self, ctx: Context, *,
            expression: str = commands.parameter(description='String with the expression')) -> None:

        # Wait message
        await ctx.defer()

        # Need imports
        getattr(sys, 'set_int_max_str_digits', lambda _: None)(0)

        # Get expression from string
        try:
            expr: sympy.Expr | str = sympy.parse_expr(
                expression, evaluate=True, transformations=sympy.parsing.sympy_parser.T[:])
            assert expr is not None
        except (SyntaxError, AssertionError, ValueError):
            result = ['Syntax Error']
        except Exception as e:
            result = [type(e).__name__]
        else:

            # Calculating expression
            try:
                fn = float(n := str(expr.evalf(30)))
                number = f'{fn:.30g}' if expr.is_number else n
            except (SyntaxError, AttributeError, ValueError):
                result = [str(expr), 'Value Error']
            except Exception as e:
                result = [str(expr), type(e).__name__]
            else:
                result = [str(expr), number] if not expr.is_number else [
                    number]

        # Work with data | ```py\n{}\n```, max=1024 -> 6 + x + 4 ==> x <= 1014
        if len(expression) > 1014:
            expression = '{}...'.format(expression[:1011])
        for element in range(len(result)):
            if len(result[element]) > 1014:
                result[element] = 'Value Error'

        # Output
        embed = Embed(title='Math Calculator', description='Based on SymPy')
        embed.add_field(name='Your expression:',
                        value='```py\n%s\n```' % expression, inline=False)
        if len(result) > 1 and result[0] != result[1]:
            embed.add_field(name='Simplified view:',
                            value='```py\n%s\n```' % result.pop(0))
        embed.add_field(name='Detailed result:',
                        value='```py\n%s\n```' % result.pop(0))
        embed.set_author(
            name='by %s' % getattr(ctx.author, 'display_name', 'People'),
            icon_url=getattr(ctx.author.avatar, 'url', ''))

        # Send
        await ctx.send(embed=embed)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Calculator(bot))
