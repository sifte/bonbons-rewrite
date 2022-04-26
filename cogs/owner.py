import contextlib
import io
import textwrap
import traceback

import discord
from discord.ext import commands

from helpers.bot import Bonbons
from helpers.paginator import Paginator


class TextPaginator:

    __slots__ = ("data", "ctx")

    def __init__(self, ctx: commands.Context, data: list):
        self.ctx = ctx
        self.data = data

    async def start(self):
        embeds = []

        for index, result in enumerate(self.data):
            embed = discord.Embed(
                description=f"```py\n{result}\n```", color=discord.Color.blurple()
            ).set_footer(text=f"Page {index+1}/{len(self.data)}")
            embeds.append(embed)

        view = Paginator(self.ctx, embeds, embed=True)

        view.msg = await self.ctx.reply(embed=embeds[0], view=view)


class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def cleanup_code(content: str) -> str:
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])
        return content.strip("` \n")

    async def cog_check(self, ctx: commands.Context) -> bool:
        return ctx.author.id == 656073353215344650

    @commands.command(name="eval", aliases=("e",))
    async def _eval(self, ctx: commands.Context, *, code: str) -> None:

        global_vars = {
            "ctx": ctx,
            "bot": self.bot,
            "discord": discord,
            "_channel": ctx.channel,
            "_author": ctx.author,
            "_guild": ctx.guild,
            "_message": ctx.message,
            "nl": "\n",
            **globals(),
        }

        code = self.cleanup_code(code)
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):

                exec(
                    f'async def _eval():\n{textwrap.indent(code, "  ")}',
                    global_vars,
                )
                obj = await global_vars["_eval"]()
                result = str(obj).replace(self.bot.http.token, "[TOKEN]")

        except Exception as e:
            result = "".join(traceback.format_exception(e, e, e.__traceback__))

        if len(result) >= 4000:
            paginator = TextPaginator(
                ctx, [result[i : i + 4000] for i in range(0, len(result), 4000)]
            )
            return await paginator.start()

        if result == "None":
            return

        embed = discord.Embed(
            description=f"```py\n{result}\n```", color=discord.Color.blurple()
        )
        await ctx.reply(embed=embed)

    @commands.Cog.listener("on_message_edit")
    async def _re_invoke_owner_commands(
        self, before: discord.Message, after: discord.Message
    ) -> None:

        context = await self.bot.get_context(after)
        prefix = context.prefix

        valid_messages = (f"{prefix}eval", f"{prefix}e", f"{prefix}jsk py")

        if after.content.startswith(valid_messages):
            await self.bot.process_commands(after)


async def setup(bot: Bonbons):
    print("Loaded: Owner")
    await bot.add_cog(Owner(bot))
