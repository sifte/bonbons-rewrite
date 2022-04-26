from datetime import datetime

import discord
from discord.ext import commands


class Starboard(commands.Cog, description="Starboard related commands."):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.mongo["discord"]["config"]
        self.sb = self.bot.mongo["discord"]["starboard"]

    @property
    def emoji(self):
        return "⭐"

    async def set_starboard_count(self, ctx, count):

        """Sets the reactions needed to be on the starboard."""

        data = await self.config.find_one({"_id": ctx.guild.id})

        if not data:
            return await ctx.send(
                "This server has no starboard channel yet. Do `.starboard set #channel`"
            )

        if data:
            await self.config.update_one(
                {"_id": ctx.guild.id}, {"$set": {"reactions": count}}
            )
            return await ctx.send(
                f"I have set the reactions needed for the starboard to `{count}`."
            )

    async def add_to_starboard(self, reaction, user):

        """Adds something to the starboard."""

        if reaction.message.embeds:
            return

        reactions = await self.config.find_one({"_id": reaction.message.guild.id})

        if reactions is None:
            return

        starboard_channel_id = reactions["channel"]
        starboard_channel = self.bot.get_channel(
            starboard_channel_id
        ) or await self.bot.fetch_channel(starboard_channel_id)

        data = await self.sb.find_one({"_id": reaction.message.id})
        if data:
            data_channel = data["channel"]

            msg = self.bot.get_message(
                data["starboard_message"]
            ) or await self.bot.fetch_message(data["starboard_message"])
            await msg.edit(
                content=f"⭐ **{reaction.count}** <#{data_channel}> ID: {data['_id']}"
            )

        if not data:
            if reaction.emoji == "⭐" and reaction.count > reactions["reactions"]:

                em = discord.Embed(
                    description=reaction.message.content,
                    color=discord.Color.blurple(),
                    timestamp=datetime.utcnow(),
                )
                em.set_author(
                    name=reaction.message.author,
                    icon_url=reaction.message.author.display_avatar,
                )

                if reaction.message.attachments:
                    em.set_image(url=reaction.message.attachments[0].url)
                bot_msg = await starboard_channel.send(
                    content=f"⭐ **{reaction.count}** <#{reaction.message.channel.id}> ID: {reaction.message.id}",
                    embed=em,
                )
                await self.sb.insert_one(
                    {
                        "_id": reaction.message.id,
                        "channel": reaction.message.channel.id,
                        "author": reaction.message.author.id,
                        "content": reaction.message.content,
                        "starboard_message": bot_msg.id,
                    }
                )

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        await self.add_to_starboard(reaction, user)

    @commands.group(invoke_without_command=True)
    async def starboard(self, ctx):
        """The base command for starboard."""
        await ctx.send_help("starboard")

    @starboard.command()
    @commands.has_permissions(manage_channels=True)
    async def reactions(self, ctx, count: int):
        """Sets the reactions needed for the starboard."""

        if not ctx.author.guild_permissions.manage_channels:
            return await ctx.send(
                "You do not have enough permissions to set the starboard channel."
            )

        await self.set_starboard_count(ctx, count)

    @starboard.command()
    async def show(self, ctx, message: int):
        """Shows a message that's been starboard'd"""
        ...

    @starboard.command()
    async def info(self, ctx):
        """Display's the server's starboard information."""
        data = await self.config.find_one({"_id": ctx.guild.id})
        if data:
            embed = discord.Embed(
                title="Starboard Information",
                description=f"• **Channel:** <#{data['channel']}>\n• **Reactions Needed:** {data['reactions']}",
                color=discord.Color.blurple(),
                timestamp=discord.utils.utcnow(),
            )

            await ctx.send(embed=embed)
        if not data:
            await ctx.send("This server has no starboard setup yet.")

    @starboard.command()
    @commands.has_permissions(manage_channels=True)
    async def set(self, ctx, channel: discord.TextChannel):
        """Sets a channel to be the starboard."""
        data = await self.config.find_one(
            {
                "_id": ctx.guild.id,
            }
        )

        if not ctx.author.guild_permissions.manage_channels:
            return await ctx.send(
                "You do not have enough permissions to set the starboard channel."
            )

        if data:
            await self.config.update_one(
                {"_id": ctx.guild.id}, {"$set": {"channel": channel.id}}
            )
            return await ctx.send(
                f"I have set the channel for the starboard to {channel.mention}"
            )

        if not data:
            await self.config.insert_one(
                {
                    "_id": ctx.guild.id,
                    "channel": channel.id,
                    "reactions": 5,
                }
            )

            await ctx.send(
                f"I have set the channel for the starboard to {channel.mention}"
            )


def setup(bot):
    bot.add_cog(Starboard(bot))
