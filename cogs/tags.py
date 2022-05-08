import copy
from datetime import datetime
from typing import Union

import discord
from discord.ext import commands

from helpers.bot import Bonbons
from helpers.tags.engine import TagEngine

class Tags(commands.Cog):

    """A cog for tags."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = self.bot.mongo["tags"]

    @property
    def emoji(self) -> str:
        return "🏷️"

    async def cog_check(self, ctx: commands.Context) -> bool:
        return ctx.guild is not None

    @commands.group(name="tag", invoke_without_command=True, case_insensitive=True)
    async def tag(self, ctx: commands.Context, name: Union[str, int] = None) -> None:

        """Sends help for the tag group, sends a tag's content if an argument was passed."""

        if name is not None:
            db = self.db[str(ctx.guild.id)]

            tag = await db.find_one({"name": name}) or await db.find_one({"_id": name})
            

            if tag is not None:
                engine = TagEngine(ctx)
                return await ctx.send(engine.substitute(tag["content"]))

            elif tag is None:
                return await ctx.send(f"A tag with the name `{name}` does not exist.")

        if name is None:
            await ctx.send_help("tag")

    @tag.command(name="create", aliases=("new",))
    async def create(self, ctx: commands.Context, name: str, *, content: str) -> None:

        """Create a tag."""

        db = self.db[str(ctx.guild.id)]
        tag = await db.find_one({"name": name})
        tag_id = len(await db.find().to_list(10000)) + 1

        if tag is not None:
            return await ctx.send("A tag with this name already exists.")

        tag_data = {
            "_id": tag_id,
            "owner": ctx.author.id,
            "name": name,
            "content": content,
            "created": int(datetime.now().timestamp()),
        }

        await db.insert_one(tag_data)
        return await ctx.send(
            f"Tag successfully created. Do `{ctx.clean_prefix}tag {name}` to view the tag!"
        )

    @tag.command(name="info")
    async def information(self, ctx: commands.Context, *, name: str) -> None:

        """Get information about a tag."""

        db = self.db[str(ctx.guild.id)]

        tag = await db.find_one({"name": name.lower()})

        if tag is not None:
            owner = self.bot.get_user(tag["owner"]) or await self.bot.fetch_user(
                tag["owner"]
            )
            embed = discord.Embed(title=tag["name"], color=discord.Color.random())
            embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar)
            embed.add_field(name="Owner", value=f"{owner.mention} ({owner}")

            return await ctx.send(embed=embed)

        if tag is None:
            return await ctx.reply("Not a valid tag!")

    @tag.command(name="edit")
    async def edit(self, ctx: commands.Context, name: str, *, content: str) -> None:

        """Edits a tag."""

        db = self.db[str(ctx.guild.id)]
        tag = await db.find_one({"name": name})

        if tag is None:
            return await ctx.send("A tag with that name does not exist!")

        if ctx.author.id != tag["owner"]:
            return await ctx.send("You do not own this tag.")

        await self.db.update_one({"name": name}, {"$set": {"content": content}})

        await ctx.send(
            f"tag successfully edited! Do `{ctx.clean_prefix}tag {name}` to view the tag."
        )

    @tag.command(name="all", aliases=("list",))
    async def all(self, ctx: commands.Context) -> None:

        """Get all the tags in the current server."""

        db = self.db[str(ctx.guild.id)]
        tags = []

        async for tag in db.find():
            tags.append(tag["name"])

        if len(tags) == 0:
            return await ctx.send("There are no tags in this server.")

        await ctx.send(
            f'```\nTags for {ctx.guild.name} | ID: {ctx.guild.id} | Total tags: {len(tags)}\n------------------------------------------------------------------------\n{", ".join(tags)}```'
        )
        # i don't know any other way to do this without making it long

    @tag.command(name="delete", aliases=("remove",))
    async def delete(self, ctx: commands.Context, *, name: str) -> None:

        """Delete a tag."""

        db = self.db[str(ctx.guild.id)]

        tag = await db.find_one({"name": name})

        if tag is not None:
            if tag["owner"] == ctx.author.id:
                return await db.delete_one({"name": tag["name"]})

            return await ctx.reply("You do not own this tag.")

        if tag is None:
            return await ctx.reply("A tag with this name does not exist.")

    @tag.command(name="variables", aliases=("vars", "substitutes"))
    async def variables(self, ctx: commands.Context):
        engine = TagEngine(ctx)
        embed = discord.Embed(title="Variables", description="\n".join(engine.substitutes.keys()))
        
    @commands.Cog.listener("on_message")
    async def send_tag(self, message: discord.Message) -> None:

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
                tag = await db.find_one({"name": new_content}) or await db.find_one(
                    {"name": new_content.lower()}
                )

                if tag is None:
                    return await self.bot.process_commands(msg)

                msg.content = f"{ctx.prefix}tag {new_content}"

                await self.bot.process_commands(msg)


async def setup(bot: Bonbons) -> None:
    print("Loaded: Tags")
    await bot.add_cog(Tags(bot))
