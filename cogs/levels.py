import io
import random
import time
from datetime import datetime

import discord
from discord.ext import commands
from easy_pil import Canvas, Editor, Font, load_image_async
from tabulate import tabulate

from helpers.bot import Bonbons


class Levels(commands.Cog):

    """
    A cog for levels.
    """

    def __init__(self, bot: Bonbons) -> None:
        self.bot = bot
        self.db = self.bot.mongo["levels"]
        self.levels: dict[int, int] = {}
        self.make_levels()
        self.set_attributes()

    @property
    def emoji(self) -> str:
        return "⬆️"

    def make_levels(self) -> None:
        for number in range(500):
            self.levels[number] = 125 * number

    def set_attributes(self) -> None:
        self.bot.generate_rank_card = self.generate_rank_card
        self.bot.generate_leaderboard = self.generate_leaderboard

    async def generate_rank_card(
        self, ctx: commands.Context, member: discord.Member, data, background=None
    ) -> None:
        next_level_xp = self.levels[int(data["level"]) + 1]
        percentage = (data["xp"] / next_level_xp) * 100
        user_data = {
            "name": str(member),
            "xp": int(data["xp"]),
            "next_level_xp": next_level_xp,
            "level": int(data["level"]),
            "percentage": int(percentage),
        }

        if background:
            background = Editor(await load_image_async(str(background))).resize(
                (800, 280)
            )
        else:
            background = Editor(Canvas((800, 280), color="#23272A"))

        profile_image = await load_image_async(str(member.display_avatar.url))
        profile = Editor(profile_image).resize((150, 150)).circle_image()

        poppins = Font.poppins(size=40)
        poppins_small = Font.poppins(size=30)

        card_right_shape = [(600, 0), (750, 300), (900, 300), (900, 0)]

        background.polygon(card_right_shape, "#2C2F33")
        background.paste(profile, (30, 30))

        background.rectangle((30, 200), width=650, height=40, fill="#494b4f", radius=20)
        background.bar(
            (30, 200),
            max_width=650,
            height=40,
            percentage=user_data["percentage"],
            fill="#3db374",
            radius=20,
        )
        background.text((200, 40), user_data["name"], font=poppins, color="white")

        background.rectangle((200, 100), width=350, height=2, fill="#17F3F6")
        background.text(
            (200, 130),
            f"Level: {user_data['level']} "
            + f" XP: {user_data['xp']: ,} / {user_data['next_level_xp']: ,}",
            font=poppins_small,
            color="white",
        )

        with io.BytesIO() as buffer:
            background.save(buffer, "PNG")
            buffer.seek(0)

            embed = discord.Embed(color=discord.Color.blurple())
            embed.set_image(url="attachment://rank_card.png")
            return await ctx.send(
                file=discord.File(buffer, "rank_card.png"), embed=embed
            )

    async def generate_leaderboard(self, ctx: commands.Context) -> None:

        before = time.perf_counter()
        background = Editor(Canvas((1400, 1280), color="#23272A"))
        db = self.db[str(ctx.guild.id)]
        paste_size = 0
        text_size = 40

        for x in await db.find().sort("level", -1).to_list(10):

            user = self.bot.get_user(x["_id"]) or await self.bot.fetch_user(x["_id"])

            if user.avatar is None:
                img = Editor(await load_image_async(str(user.display_avatar))).resize(
                    (128, 128)
                )
            else:
                img = await load_image_async(
                    str(user.display_avatar.with_size(128).with_format("png"))
                )

            background.text(
                (175, text_size),
                f'{str(user)} • Level{x["level"]: ,}',
                color="white",
                font=Font.poppins(size=50),
            )

            background.paste(img, (0, paste_size))
            paste_size += 128
            text_size += 130

        with io.BytesIO() as buffer:
            background.save(buffer, "PNG")
            buffer.seek(0)

            done = time.perf_counter() - before

            embed = discord.Embed(
                title=f"{ctx.guild.name} Level Leaderboard",
                description="This is based off of your level and not XP.",
                color=discord.Color.blurple(),
                timestamp=datetime.utcnow(),
            )
            embed.set_image(url="attachment://leaderboard.png")
            embed.set_footer(text=f"Took{done: .2f}s")

            return await ctx.send(
                file=discord.File(buffer, "leaderboard.png"), embed=embed
            )

    @commands.command(name="rank", aliases=("level",))
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def rank(self, ctx: commands.Context, member: discord.Member = None):
        """Tells you your current level embedded inside an image."""

        member = member or ctx.author

        db = self.db[str(ctx.guild.id)]

        data = await db.find_one({"_id": member.id})

        if data is not None:
            return await self.generate_rank_card(ctx, member, data)

        await ctx.reply(
            "You have no XP somehow. Send some more messages into the chat and try again.."
        )

    @commands.command(name="setlevel")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def setlevel(self, ctx: commands.Context, member: discord.Member, level: int):

        db = self.db[str(ctx.guild.id)]

        data = await db.find_one({"_id": member.id})

        if data is not None:
            await self.db.update_one({"_id": data["_id"]}, {"$set": {"level": level}})
            return await ctx.reply(f"{member}'s level has been set to {level}.")

    @commands.command(name="leaderboard", aliases=("lb",))
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def leaderboard(self, ctx: commands.Context, args: str = None):
        """Shows the level leaderboard for the current server."""

        if args:
            if args == "--text" or args == "--all":
                data = {"level": [], "xp": [], "id": []}
                db = self.db[str(ctx.guild.id)]

                async for doc in db.find().sort("level", -1):
                    data["level"].append(doc["level"])
                    data["xp"].append(doc["xp"])
                    data["id"].append(doc["_id"])

                content = tabulate(
                    {"ID": data["id"], "Level": data["level"], "XP": data["xp"]},
                    ["ID", "Level", "XP"],
                    tablefmt="pretty",
                )
                file = discord.File(
                    io.BytesIO(content.encode("utf-8")), filename="text.txt"
                )
                return await ctx.send(file=file)
            else:
                pass

        await self.generate_leaderboard(ctx)

    @commands.Cog.listener("on_message")
    async def handle_message(self, message: discord.Message):

        if message.author.bot:
            return

        if not isinstance(message.channel, discord.TextChannel):
            return

        db = self.db[str(message.guild.id)]

        data = await db.find_one({"_id": message.author.id})
        xp = random.randint(10, 200)

        if data is not None:

            next_level = data["level"] + 1
            next_level_xp = self.levels[next_level]

            if int(data["xp"]) >= int(next_level_xp):
                await db.update_one({"_id": message.author.id}, {"$inc": {"level": 1}})
                await db.update_one(
                    {"_id": message.author.id}, {"$set": {"xp": xp / 2}}
                )
                return

            await db.update_one({"_id": message.author.id}, {"$inc": {"xp": xp}})
            return

        if data is None:
            await db.insert_one({"_id": message.author.id, "xp": xp, "level": 1})
            return


async def setup(bot):
    print("Loaded: Levels")
    await bot.add_cog(Levels(bot))
