import re
from datetime import timedelta

import discord
from discord.ext import commands, tasks


class TimeConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> float:
        time_regex = re.compile(r"(\d{1,5}(?:[.,]?\d{1,5})?)([smhd])")
        time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
        matches = time_regex.findall(argument.lower())
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument(
                    f"{k} is an invalid time-key! h/m/s/d are valid!"
                )
            except ValueError:
                raise commands.BadArgument(f"{v} is not a number!")
        return time


class Reminders(commands.Cog):
    """
    Reminders that remind you to do something in the future.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.check_for_reminders.start()
        self.base = self.bot.mongo["reminders"]
        self._channels: dict[int, discord.TextChannel] = {}

    @property
    def emoji(self) -> str:
        return "⏲️"

    @staticmethod
    def parse_time(time: int, *, timestamp: bool = False) -> str:
        data = discord.utils.utcnow() + timedelta(seconds=time)

        if timestamp:
            return int(data.timestamp())

        return f"<t:{int(data.timestamp())}:F>"

    async def add_reminder(self, ctx: commands.Context, time: int, reason: str) -> None:
        db = self.base[str(ctx.guild.id)]

        await db.insert_one(
            {
                "author": ctx.author.id,
                "time": time,
                "channel": ctx.channel.id,
                "reason": reason,
            }
        )

    @commands.command(name="remind", aliases=("r",))
    async def remind(
        self, ctx: commands.Context, time: TimeConverter, *, reminder: str
    ):

        parsed_time = self.parse_time(time, timestamp=False)
        reminder_time = self.parse_time(time, timestamp=True)
        await ctx.send(f"I will remind you at {parsed_time}.")
        self._channels[ctx.channel.id] = ctx.channel

        await self.add_reminder(ctx, reminder_time, reminder)

    @tasks.loop(seconds=10)
    async def check_for_reminders(self) -> None:

        await self.bot.wait_until_ready()

        for item in await self.base.list_collections():

            for result in await self.base[item["name"]].find().to_list(100000):
                if int(discord.utils.utcnow().timestamp()) > result["time"]:
                    collection = self.base[item["name"]]
                    channel = self._channels.get(
                        result["channel"]
                    ) or await self.bot.fetch_channel(result["channel"])

                    member = f"<@{result['author']}>"

                    await channel.send(f"Hey {member}, {result['reason']}")

                    await collection.delete_one({"author": result["author"]})


async def setup(bot: commands.Bot):
    await bot.add_cog(Reminders(bot))
