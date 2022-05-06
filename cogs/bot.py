import discord
from discord.ext.commands import Cog, Context, command

from helpers.bot import Bonbons


class Bot(Cog):

    """
    A cog for commands related to me.
    """

    def __init__(self, bot: Bonbons) -> None:
        self.bot = bot

    @property
    def emoji(self) -> str:
        return "🤖"

    @command(name="information", aliases=("uptime", "info"))
    async def info(self, ctx: Context) -> None:

        """Gives you information about me."""

        users = len(self.bot.users)
        guilds = len(self.bot.guilds)

        embed = discord.Embed(title="Info", color=discord.Color.blurple())

        embed.description = f"• Guilds: {guilds:,}\n• Users: {users:,}\n• Uptime: <t:{int(self.bot.uptime)}:F> (<t:{int(self.bot.uptime)}:R>)\n• Latency: {int(self.bot.latency * 1000):.2f}ms"
        await ctx.send(embed=embed)

    @command(name="ping")
    async def ping(self, ctx: Context) -> None:

        """Pong? TwT 🏓"""

        latency = f"{self.bot.latency * 1000:.2f}ms"

        await ctx.send(latency)


async def setup(bot: Bot):
    print("Loaded: Bot")
    await bot.add_cog(Bot(bot))
