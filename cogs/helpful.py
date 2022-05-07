import asyncio
import re

import discord
import googletrans
from discord.ext import commands
from pyston import File, PystonClient

CODE_REGEX = re.compile(r"(\w*)\s*(?:```)(\w*)?([\s\S]*)(?:```$)")
NEWLINE_LIMIT = 15
SLICE_LIMIT = 300


class Helpful(commands.Cog):

    """Helpful commands."""

    def __init__(self, bot):
        self.pysclient = PystonClient()
        self.bot = bot
        self.runs = {}
        self.translator = googletrans.Translator()

    @property
    def emoji(self) -> str:
        return "😄"

    @staticmethod
    def parse_content(content: str, lang: str) -> str:

        if lang:
            return content.replace("```", "", 2).replace(lang, "", 1)

        return content.replace("```", "", 2)

    async def run_code(self, ctx: commands.Context, lang: str, code: str) -> None:
        try:
            lang = lang.split("```")[1]
            code = code.split("```")[0]
            output = await self.pysclient.execute(
                str(lang), [File(self.parse_content(code, lang))]
            )

            if (
                output.raw_json["run"]["stdout"] == ""
                and output.raw_json["run"]["stderr"]
            ):
                self.runs[ctx.author.id] = await ctx.reply(
                    content=f"{ctx.author.mention} :warning: Your {lang} job has completed with return code 1.\n\n```{lang}\n{output}\n```"
                )
                return

            if output.raw_json["run"]["stdout"] == "":
                self.runs[ctx.author.id] = await ctx.send(
                    content=f"{ctx.author.mention} :warning: Your {lang} job has completed with return code 0.\n\n```{lang}\n[No output]\n```"
                )
                return

            else:

                if str(output).count("\n") >= NEWLINE_LIMIT:
                    output = (
                        str(output)[:SLICE_LIMIT] + "\n... (truncated, too many lines)"
                    )

                self.runs[ctx.author.id] = await ctx.send(
                    content=f"{ctx.author.mention} :white_check_mark: Your {lang} job has completed with return code 0.\n\n```{lang}\n{output}\n```"
                )
                return

        except Exception:
            output = await self.pysclient.execute(
                lang, [File(self.parse_content(code, lang))]
            )

            if (
                output.raw_json["run"]["stdout"] == ""
                and output.raw_json["run"]["stderr"]
            ):
                self.runs[ctx.author.id] = await ctx.reply(
                    content=f"{ctx.author.mention} :warning: Your {lang} job has completed with return code 1.\n\n```{lang}\n{output}\n```"
                )
                return

            if output.raw_json["run"]["stdout"] == "":
                self.runs[ctx.author.id] = await ctx.send(
                    content=f"{ctx.author.mention} :warning: Your {lang} job has completed with return code 0.\n\n```{lang}\n[No output]\n```"
                )
                return

            else:
                if str(output).count("\n") >= NEWLINE_LIMIT:
                    output = (
                        str(output)[:SLICE_LIMIT] + "\n... (truncated, too many lines)"
                    )

                self.runs[ctx.author.id] = await ctx.send(
                    content=f"{ctx.author.mention} :white_check_mark: Your {lang} job has completed with return code 0.\n\n```{lang}\n{output}\n```"
                )
                return

    @commands.command(name="run")
    async def run(self, ctx: commands.Context, language: str, *, code: str):
        """Run some code."""
        async with ctx.typing():
            lang = await commands.clean_content().convert(ctx, language)
            code = await commands.clean_content().convert(ctx, code) 

            await self.run_code(ctx, language, code)

    @commands.command(name="translate")
    async def translate(
        self, ctx: commands.Context, *, message: commands.clean_content = None
    ):
        """Translates a message using google translate."""

        if message is None:
            ref = ctx.message.reference
            if ref and isinstance(ref.resolved, discord.Message):
                message = ref.resolved.content
            else:
                return await ctx.send("Missing a message to translate.")

        try:
            ret = await self.bot.loop.run_in_executor(
                None, self.translator.translate, message
            )
        except Exception as e:
            return await ctx.send(f"An error occurred: {e.__class__.__name__}: {e}")

        embed = discord.Embed(title="Translated", colour=0x4284F3)
        src = googletrans.LANGUAGES.get(ret.src, "(auto-detected)").title()
        dest = googletrans.LANGUAGES.get(ret.dest, "Unknown").title()
        embed.add_field(name=f"From {src}", value=ret.origin, inline=False)
        embed.add_field(name=f"To {dest}", value=ret.text, inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    print("Loaded: Helpful")
    await bot.add_cog(Helpful(bot))
