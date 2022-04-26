from datetime import datetime

import discord
from discord.ext import commands


class Information(commands.Cog):

    """
    Information related commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @property
    def emoji(self) -> str:
        return "ℹ️"

    @staticmethod
    def created_at(value: id) -> int:
        obj = discord.Object(value)
        return f"{discord.utils.format_dt(obj.created_at, 'F')} ({discord.utils.format_dt(obj.created_at, 'R')})"

    @commands.command(name="snowflake")
    async def snowflake(self, ctx: commands.Context, id: int) -> None:

        """Tells you a snowflake's creation date."""

        try:
            embed = discord.Embed(
                description=f"Snowflake was created at {self.created_at(id)}",
                color=discord.Color.blurple(),
            )
            await ctx.send(embed=embed)
        except ValueError:
            return await ctx.send(
                embed=discord.Embed(
                    description="That is not a valid snowflake.",
                    color=discord.Color.red(),
                )
            )

        else:
            return

    @commands.command(name="avatar", aliases=("av",))
    @commands.guild_only()
    async def avatar(
        self, ctx: commands.Context, *, member: discord.Member = None
    ) -> None:

        """
        Display's a member's avatar.
        """

        member = member or ctx.author

        embed = discord.Embed(color=discord.Color.blurple())
        embed.set_image(url=member.display_avatar)
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)

    @commands.command(name="serverinfo")
    @commands.guild_only()
    async def serverinfo(self, ctx: commands.Context) -> None:

        """
        Returns information about the current server.
        """

        embed = discord.Embed(
            title=ctx.guild.name,
            description=f"**ID:** {ctx.guild.id}\n**Owner:** {ctx.guild.owner}",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(
            name="Server Created At",
            value=f"{discord.utils.format_dt(ctx.guild.created_at, 'F')} ({discord.utils.format_dt(ctx.guild.created_at, 'R')})",
            inline=False,
        )
        embed.add_field(
            name="Information",
            value=f"• Members: {len(ctx.guild.members)}\n• Channels: {len(ctx.guild.channels)}\n• Emojis: {len(ctx.guild.emojis)}",
        )

        if len(str(ctx.guild.roles)) >= 1000:
            embed.add_field(
                name=f"Server Roles [{len(ctx.guild.roles)}]",
                value="There are too many roles to display.",
                inline=False,
            )
        else:
            embed.add_field(
                name=f"Server Roles [{len(ctx.guild.roles)}]",
                value=" ".join(r.mention for r in ctx.guild.roles[::-1]),
                inline=False,
            )

        if ctx.guild.icon is None:
            return await ctx.send(embed=embed)

        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    @commands.command(name="whois", aliases=("userinfo", "u"))
    @commands.guild_only()
    async def whois(
        self, ctx: commands.Context, *, member: discord.Member = None
    ) -> None:

        """
        Tells you information about a member.
        """

        member = member or ctx.author

        roles = " ".join([role.mention for role in member.roles[::-1]])

        embed = discord.Embed(
            description=f"**Member:** {member.mention}\n**ID:** {member.id}",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        embed.set_thumbnail(url=member.display_avatar)
        embed.set_author(
            name=member,
            icon_url=member.display_avatar,
        )
        embed.add_field(
            name="Account Created At",
            value=f"{self.created_at(member.id)}",
            inline=False,
        )
        embed.add_field(
            name="Joined Server At",
            value=f"<t:{int(member.joined_at.timestamp())}:F> (<t:{int(member.joined_at.timestamp())}:R>)",
            inline=False,
        )
        embed.add_field(
            name=f"Roles [{len(member.roles)-1}]",
            value=roles,
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command(name="spotify")
    @commands.guild_only()
    async def spotify(
        self, ctx: commands.Context, member: discord.Member = None
    ) -> None:

        """
        Shows you a member's spotify activity
        """

        member = member or ctx.author

        for activity in member.activities:
            if isinstance(activity, discord.Spotify):
                embed = discord.Embed(
                    title=f"{member.name}'s Spotify",
                    description=f"**Track ID:** {activity.track_id}",
                    color=0x1DB954,
                    timestamp=datetime.utcnow(),
                )
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.add_field(name="Song", value=activity.title)
                embed.add_field(name="Artist", value=activity.artist)
                embed.add_field(name="Album", value=activity.album, inline=False)
                embed.set_footer(
                    text=ctx.author, icon_url=ctx.author.display_avatar.url
                )
                await ctx.send(embed=embed)

        if not member.activity:
            await ctx.send("Member does not have a spotify activity.")

    @commands.command(name="roleinfo")
    @commands.guild_only()
    async def roleinfo(self, ctx: commands.Context, role: discord.Role = None) -> None:

        """
        Tells you information about a role, will use your top role if no role was passed.
        """

        role_mentionable = None
        role_hoisted = None

        role = role or ctx.author.top_role

        x = "❌"
        check = "✅"

        if role.mentionable:
            role_mentionable = check

        if role.hoist is True:
            role_hoisted = check

        if role.mentionable is False:
            role_mentionable = x

        if role.hoist is False:
            role_hoisted = x

        embed = discord.Embed()
        embed.description = f"**Role:** {role.mention}\n**ID:** {role.id}"
        embed.color = role.color
        embed.timestamp = datetime.utcnow()

        embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar)
        embed.add_field(
            name="Role Created At",
            value=f"<t:{int(role.created_at.timestamp())}:F> (<t:{int(role.created_at.timestamp())}:R>)",
            inline=False,
        )
        embed.add_field(
            name="Features",
            value=f"• Color: {role.color}\n• Members: {len(role.members)}\n• Position: {str(role.position)}/{len(ctx.guild.roles)}\n• Hoisted: {role_hoisted}\n• Mentionable: {role_mentionable}",
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command(name="channelinfo")
    @commands.guild_only()
    async def channelinfo(self, ctx, channel: discord.abc.GuildChannel = None):

        """
        Tells you information about a discord channel.
        """

        channel = channel or ctx.channel

        embed = discord.Embed(
            description=f"**Channel:** {channel.mention}\n**ID:** {channel.id}",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar)
        embed.add_field(
            name="Channel Created At",
            value=f"<t:{int(channel.created_at.timestamp())}:F> (<t:{int(channel.created_at.timestamp())}:R>)",
            inline=False,
        )
        embed.add_field(
            name="Features",
            value=f"• Category: {channel.category}\n• Position: {channel.position}",
            inline=False,
        )
        await ctx.send(embed=embed)


async def setup(bot):
    print("Loaded: Information")
    await bot.add_cog(Information(bot))
