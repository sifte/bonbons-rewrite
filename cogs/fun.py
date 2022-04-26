import base64
import random
from datetime import datetime
from io import BytesIO

import aiohttp
import discord
from discord.ext import commands
from simpleeval import simple_eval

from helpers.bot import Bonbons
from helpers.constants import Config
from helpers.paginator import Paginator


class Fun(commands.Cog):
    """
    Fun commands.
    """

    def __init__(self, bot: Bonbons) -> None:
        self.bot = bot
        self.snipes: list[dict] = []
        self.edits: list[dict] = []
        self.afk: dict[int, dict[int, str]] = {}

    @property
    def emoji(self) -> str:
        return "🙌"

    @staticmethod
    def parse_expressions(expressions: str) -> str:
        return expressions.replace("^", "**")

    @staticmethod
    def base64_encode(text: str):
        message_bytes = text.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        message = base64_bytes.decode("ascii")
        return message

    @staticmethod
    def base64_decode(text: str):
        b64msg = text.encode("ascii")
        message_bytes = base64.b64decode(b64msg)
        message = message_bytes.decode("ascii")
        return message

    @commands.group(
        name="base64",
        aliases=("b64",),
        invoke_without_command=True,
        case_insensitive=True,
    )
    async def base64_group(self, ctx: commands.Context) -> None:

        """
        The base command for base64.
        """

        await ctx.send_help("base64")

    @base64_group.command(name="encode")
    async def encode(self, ctx: commands.Context, *, string: str) -> None:

        """
        Encodes a string.
        """

        try:
            return await ctx.send(self.base64_encode(string))
        except Exception:
            return await ctx.send(f"Could not encode string.")

    @base64_group.command(name="decode")
    async def decode(self, ctx: commands.Context, *, string: str) -> None:

        """
        Decodes a base64 string.
        """

        try:
            return await ctx.send(self.base64_decode(string))

        except Exception:
            return await ctx.send(f"Could not decode string.")

    @commands.Cog.listener("on_message_delete")
    async def on_message_delete(self, message: discord.Message) -> None:

        if message.author.bot:
            return

        if not isinstance(message.channel, discord.TextChannel):
            return

        self.snipes.append(
            {
                "author": str(message.author),
                "channel": message.channel.id,
                "content": message.content,
                "timestamp": datetime.utcnow(),
                "msg": message,
            }
        )

    @commands.Cog.listener("on_message_edit")
    async def on_message_edit(self, before: discord.Message, after: discord.Message):

        if after.author.bot:
            return

        self.edits.append(
            {
                "author": str(before.author),
                "channel": before.channel.id,
                "content": before.content,
                "timestamp": datetime.utcnow(),
                "msg": before,
            }
        )

    @commands.command(name="editsnipe")
    async def editsnipe(self, ctx: commands.Context, id: int = None):

        """Tells you most recently edited message."""

        if len(self.edits) == 0:
            return await ctx.send("There are no recently edited messages.")

        try:
            message = self.edits[id]
        except Exception:
            message = self.edits[-1]

        if message["channel"] == ctx.channel.id:

            embed = discord.Embed(
                description=message["content"],
                timestamp=message["timestamp"],
                color=discord.Color.blurple(),
            )
            embed.set_footer(text=f"Message edited at")
            embed.set_author(
                name=message["author"],
                icon_url=message["msg"].author.display_avatar.url,
            )
            return await ctx.send(embed=embed)

        return await ctx.reply("There are no recently edited messages in this channel.")

    @commands.command(name="snipe")
    async def snipe(self, ctx: commands.Context, id: int = None):

        """Tells you the most recently deleted message."""

        if len(self.snipes) == 0:
            return await ctx.reply("There are no recently deleted messages.")

        try:
            message = self.snipes[id]
        except Exception:
            message = self.snipes[-1]

        if message["channel"] == ctx.channel.id:

            embed = discord.Embed(
                description=message["content"],
                timestamp=message["timestamp"],
            )
            embed.set_footer(text=f"Message deleted at")
            embed.set_author(
                name=message["author"],
                icon_url=message["msg"].author.display_avatar.url,
            )
            return await ctx.send(embed=embed)

        return await ctx.reply(
            "There are no recently deleted messages in this channel."
        )

    @commands.command(name="joke")
    async def joke(self, ctx: commands.Context) -> None:

        """Tells you a random joke!"""

        async with self.bot.session.get("https://some-random-api.ml/joke") as payload:
            data = await payload.json(content_type=None)
            return await ctx.send(data["joke"])

    @commands.command(name="wikipedia", aliases=("wiki",))
    async def wikipedia_cmd(self, ctx: commands.Context, *, query: str) -> None:
        """Searches for something on the wikipedia"""
        async with self.bot.session.get(
            (
                "https://en.wikipedia.org//w/api.php?action=query"
                f"&format=json&list=search&utf8=1&srsearch={query}&srlimit=5&srprop="
            )
        ) as r:
            sea = (await r.json())["query"]

            if sea["searchinfo"]["totalhits"] == 0:
                await ctx.send("Sorry, your search could not be found.")
            else:
                for x in range(len(sea["search"])):
                    article = sea["search"][x]["title"]
                    async with self.bot.session.get(
                        "https://en.wikipedia.org//w/api.php?action=query"
                        "&utf8=1&redirects&format=json&prop=info|images"
                        f"&inprop=url&titles={article}"
                    ) as r:
                        req = (await r.json())["query"]["pages"]
                        if str(list(req)[0]) != "-1":
                            break
                else:
                    await ctx.send("Sorry, your search could not be found.")
                    return
                article = req[list(req)[0]]["title"]
                arturl = req[list(req)[0]]["fullurl"]
                async with self.bot.session.get(
                    "https://en.wikipedia.org/api/rest_v1/page/summary/" + article
                ) as r:
                    artdesc = (await r.json())["extract"]
                embed = discord.discord.Embed(
                    title=f"**{article}**",
                    url=arturl,
                    description=artdesc,
                    color=0x3FCAFF,
                    timestamp=datetime.utcnow(),
                )
                embed.set_footer(
                    text=f"Search result for {query}",
                    icon_url="https://upload.wikimedia.org/wikipedia/commons/6/63/Wikipedia-logo.png",
                )
                embed.set_author(
                    name="Wikipedia",
                    url="https://en.wikipedia.org/",
                    icon_url="https://upload.wikimedia.org/wikipedia/commons/6/63/Wikipedia-logo.png",
                )
                await ctx.send(embed=embed)

    @commands.command(name="kiss", help="Kiss a user!")
    @commands.guild_only()
    async def kiss_cmd(self, ctx: commands.Context, member: discord.Member):
        await ctx.send(
            f"{ctx.author.mention} kissed {member.mention}!!\nhttps://tenor.com/view/milk-and-mocha-bear-couple-kisses-kiss-love-gif-12498627"
        )

    @commands.command(name="bonk")
    @commands.guild_only()
    async def bonk_cmd(self, ctx: commands.Context, member: discord.Member):
        """Bonk a user!"""
        bonkis = [
            "https://tenor.com/view/despicable-me-minions-bonk-hitting-cute-gif-17663380",
            "https://tenor.com/view/lol-gif-21667170",
            "https://tenor.com/view/azura-bonk-azura-bonk-gif-21733152",
        ]
        bonkiuwu = random.choice(bonkis)
        await ctx.send(f"{ctx.author.mention} bonked {member.mention}!\n{bonkiuwu}")

    @commands.command(name="spank")
    @commands.guild_only()
    async def spank_cmd(self, ctx: commands.Context, member: discord.Member):
        """Spank a user!"""
        await ctx.send(
            f"{ctx.author.mention} spanked {member.mention}!\nhttps://tenor.com/view/cats-funny-spank-slap-gif-15308590"
        )

    @commands.command(name="slap")
    @commands.guild_only()
    async def slap_cmd(self, ctx: commands.Context, member: discord.Member):
        """Slap a user!"""
        await ctx.send(
            f"{ctx.author.mention} slapped {member.mention}!\nhttps://tenor.com/view/slap-bear-slap-me-you-gif-17942299"
        )

    @commands.command(name="pat")
    @commands.guild_only()
    async def pat(self, ctx: commands.Context, member: discord.Member):
        """Pat a user!"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/animu/pat") as r:
                data = await r.json(content_type=None)
                image = data["link"]
                await ctx.send(
                    f"{ctx.author.mention} patted {member.mention}!!\n{image}"
                )

    @commands.command(name="cat")
    async def cat(self, ctx: commands.Context) -> None:
        """Sends a random cat image."""
        async with ctx.typing():
            async with self.bot.session.get("http://aws.random.cat/meow") as r:
                if r.status == 200:
                    data = await r.json()
                    await ctx.send(
                        embed=discord.Embed(color=discord.Color.blurple()).set_image(
                            url=data["file"]
                        )
                    )

    @commands.command(name="dog")
    async def dog(self, ctx: commands.Context):
        """Sends a random dog image."""
        async with ctx.typing():
            async with self.bot.session.get(
                "https://dog.ceo/api/breeds/image/random"
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    await ctx.send(
                        embed=discord.Embed(color=discord.Color.blurple()).set_image(
                            url=data["message"]
                        )
                    )

    @commands.command(name="hug")
    @commands.guild_only()
    async def hug_cmd(self, ctx: commands.Context, member: discord.Member) -> None:
        """Hug a user!"""
        async with self.bot.session.get("https://some-random-api.ml/animu/hug") as r:
            data = await r.json()
            image = data["link"]
            await ctx.send(f"{ctx.author.mention} hugged {member.mention}!!\n{image}")

    async def get_urban_response(self, ctx: commands.Context, term: str):

        headers = {
            "x-rapidapi-host": Config.HOST,
            "x-rapidapi-key": Config.KEY,
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                url="https://mashape-community-urban-dictionary.p.rapidapi.com/define",
                params={"term": term},
            ) as response:
                try:
                    data = await response.json()

                    definition, embeds = [], []

                    for item in data["list"]:
                        definition.append(
                            f'{item["word"]}\n\n**Definition:** {item["definition"]}\n\n**Author:**\n{item["author"]}'
                        )

                    for name in definition:
                        emb = discord.Embed(
                            description=name, color=discord.Color.random()
                        )
                        embeds.append(emb)

                    view = Paginator(ctx, embeds, embed=True)
                    view.msg = await ctx.send(
                        embed=embeds[0],
                        view=view,
                    )
                except IndexError:
                    return await ctx.send(
                        "I couldn't find any definitions for that word."
                    )

    @commands.command(name="define")
    async def define(self, ctx: commands.Context, term: str) -> None:
        """Defines a word."""
        await self.get_urban_response(ctx, term)

    @commands.command(name="choose")
    async def choose(self, ctx: commands.Context, *args) -> None:

        """Chooses between multiple choices."""

        await ctx.send(random.choice(args))

    @commands.command(name="calc")
    async def calc(self, ctx: commands.Context, *, expressions: str) -> None:

        """
        Tells you the result of expressions.
        """

        try:
            result = simple_eval(self.parse_expressions(expressions))

            if len(str(result)) >= 100:
                buffer = BytesIO(str(result).encode("utf-8"))
                file = discord.File(buffer, "result.txt")
                await ctx.send(
                    f"The result was too big (`{len(str(result)):,)}`), sending it to your DMs now.."
                )
                return await ctx.author.send(file=file)

            return await ctx.send(f"Result: `{result}`")

        except:
            return await ctx.send("I could not evalute expression your expression(s).")


async def setup(bot: Bonbons) -> None:
    print("Loaded: Fun")
    await bot.add_cog(Fun(bot))
