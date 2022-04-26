import copy
from datetime import datetime
from typing import Union

import discord
from discord.ext import commands

from helpers.bot import Bonbons


class Pastas(commands.Cog):

    """A cog for pastas."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = self.bot.mongo["pastas"]

    @property
    def emoji(self) -> str:
        return "🏷️"

    async def cog_check(self, ctx: commands.Context) -> bool:
        return ctx.guild is not None

    @commands.group(name="pasta", invoke_without_command=True, case_insensitive=True)
    async def pasta(self, ctx: commands.Context, name: Union[str, int] = None) -> None:

        """Sends help for the pasta group, sends a pasta's content if an argument was passed."""

        if name is not None:
            db = self.db[str(ctx.guild.id)]

            pasta = (
                await db.find_one({"name": name})
                or await db.find_one({"name": name.lower()})
                or await db.find_one({"_id": name})
            )

            if pasta is not None:
                return await ctx.send(pasta["content"])

            elif pasta is None:
                return await ctx.send("A pasta with the name `{name}` does not exist.")

        if name is None:
            await ctx.send_help("pasta")

    @pasta.command(name="create", aliases=("new",))
    async def create(self, ctx: commands.Context, name: str, *, content: str) -> None:

        """Create a pasta."""

        db = self.db[str(ctx.guild.id)]
        pasta = await db.find_one({"name": name})
        pasta_id = len(await db.find().to_list(10000)) + 1

        if pasta is not None:
            return await ctx.send("A pasta with this name already exists.")

        pasta_data = {
            "_id": pasta_id,
            "owner": ctx.author.id,
            "name": name,
            "content": content,
            "created": int(datetime.now().timestamp()),
        }

        await db.insert_one(pasta_data)
        return await ctx.send(
            f"Pasta successfully created. Do {ctx.clean_prefix}pasta {name} to view the pasta!"
        )

    @pasta.command(name="info")
    async def information(self, ctx: commands.Context, *, name: str) -> None:

        """Get information about a pasta."""

        db = self.db[str(ctx.guild.id)]

        pasta = await db.find_one({"name": name.lower()})

        if pasta is not None:
            owner = self.bot.get_user(pasta["owner"]) or await self.bot.fetch_user(
                pasta["owner"]
            )
            embed = discord.Embed(title=pasta["name"])
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar)
            embed.add_field(name="Owner", value=f"{owner.mention} ({owner}")

            return await ctx.send(embed=embed)

        if pasta is None:
            return await ctx.reply("Not a valid pasta!")

    @pasta.command(name="edit")
    async def edit(self, ctx: commands.Context, name: str, *, content: str) -> None:

        """Edits a pasta."""

        db = self.db[str(ctx.guild.id)]
        pasta = await db.find_one({"name": name})

        if pasta is None:
            return await ctx.send("A pasta with that name or ID does not exist!")

        if ctx.author.id != pasta["owner"]:
            return await ctx.send("You do not own this pasta.")

        await self.db.update_one({"name": name}, {"$set": {"content": content}})

        await ctx.send(
            f"pasta successfully edited! Do {ctx.clean_prefix}pasta {name} to view the pasta."
        )

    @pasta.command(name="all", aliases=("list",))
    async def all(self, ctx: commands.Context) -> None:

        """Get all the pastas in the current server."""

        db = self.db[str(ctx.guild.id)]
        pastas = []

        async for pasta in db.find():
            pastas.append(pasta["name"])

        if len(pastas) == 0:
            return await ctx.send("There are no pastas in this server.")

        await ctx.send(
            f'```\nPastas for {ctx.guild.name} | ID: {ctx.guild.id} | Total pastas: {len(pastas)}\n------------------------------------------------------------------------\n{", ".join(pastas)}```'
        )
        # i don't know any other way to do this without making it long

    @pasta.command(name="delete", aliases=("remove",))
    async def delete(self, ctx: commands.Context, *, name: str) -> None:

        """Delete a pasta."""

        db = self.db[str(ctx.guild.id)]

        pasta = (
            await db.find_one({"name": name})
            or await db.find_one({"name": name.lower()})
            or await db.find_one({"name": name.upper()})
        )

        if pasta is not None:
            if pasta["owner"] == ctx.author.id:
                return await db.delete_one({"name": pasta["name"]})

            return await ctx.reply("You do not own this pasta.")

        if pasta is None:
            return await ctx.reply("A pasta with this name does not exist.")

    @commands.Cog.listener("on_message")
    async def send_pasta(self, message: discord.Message) -> None:

        if isinstance(message.channel, discord.DMChannel):
            return await self.bot.process_commands(message)

        ctx = await self.bot.get_context(message)

        db = self.db[str(ctx.guild.id)]

        if (
            ctx.invoked_with
            and ctx.invoked_with.lower() not in self.bot.commands
            and ctx.command is None
        ):

            msg = copy.copy(message)

            if ctx.prefix:
                new_content = msg.content[len(ctx.prefix) :]
                pasta = await db.find_one({"name": new_content}) or await db.find_one(
                    {"name": new_content.lower()}
                )

                if pasta is None:
                    return await self.bot.process_commands(msg)

                msg.content = f"{ctx.prefix}pasta {new_content}"

                await self.bot.process_commands(msg)


async def setup(bot: Bonbons) -> None:
    print("Loaded: Pastas")
    await bot.add_cog(Pastas(bot))
