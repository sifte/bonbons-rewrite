import discord
from discord.ext.commands import Bot, Cog, Context, command, group, is_nsfw

BASE_URL = "https://api.waifu.im"


class NSFW(Cog, description="NSFW related commands."):
    def __init__(self, bot: Bot):
        self.bot = bot

    @property
    def emoji(self) -> str:
        return "🔞"

    async def _get_nsfw_image(self, ctx: Context, type: str) -> discord.Embed:
        url = f"{BASE_URL}/random/?selected_tags={type}&nsfw=true"

        async with self.bot.session.get(url) as response:
            data = (await response.json())["images"][0]

            embed = discord.Embed(color=discord.Color.blurple())
            embed.set_author(
                name=str(ctx.author),
                icon_url=ctx.author.display_avatar,
                url=data["source"],
            )
            embed.set_image(url=data["url"])

            return embed

    async def _get_sfw_image(self, ctx: Context, type: str) -> discord.Embed:
        url = f"{BASE_URL}/random/?selected_tags={type}"

        async with self.bot.session.get(url) as response:
            data = (await response.json())["images"][0]

            embed = discord.Embed(color=discord.Color.blurple())
            embed.set_author(
                name=str(ctx.author),
                icon_url=ctx.author.display_avatar,
                url=data["source"],
            )
            embed.set_image(url=data["url"])

            return embed

    @group(name="nsfw", invoke_without_command=True, case_insensitive=True)
    @is_nsfw()
    async def nsfw(self, ctx: Context):
        """The base command for all the NSFW commands."""
        await ctx.send_help("nsfw")

    @nsfw.command(name="ass")
    @is_nsfw()
    async def ass(self, ctx: Context):
        """Ass focused content."""
        img = await self._get_nsfw_image(ctx, "ass")
        await ctx.send(embed=img)

    @nsfw.command(name="erotic", aliases=("ero",))
    @is_nsfw()
    async def erotic(self, ctx: Context):
        """Erotic content."""
        img = await self._get_nsfw_image(ctx, "ero")
        await ctx.send(embed=img)

    @nsfw.command(name="hentai")
    @is_nsfw()
    async def hentai(self, ctx: Context):
        """Any kind of erotic content."""
        img = await self._get_nsfw_image(ctx, "hentai")
        await ctx.send(embed=img)

    @nsfw.command(name="maid")
    @is_nsfw()
    async def maid(self, ctx: Context):
        """Sexy womans or girl employed to do domestic work in their working uniform."""
        img = await self._get_nsfw_image(ctx, "maid")
        await ctx.send(embed=img)

    @nsfw.command(name="milf")
    @is_nsfw()
    async def milf(self, ctx: Context):
        """A sexually attractive middle-aged woman."""
        img = await self._get_nsfw_image(ctx, "milf")
        await ctx.send(embed=img)

    @nsfw.command(name="oppai")
    @is_nsfw()
    async def oppai(self, ctx: Context):
        """Boobs focused content."""
        img = await self._get_nsfw_image(ctx, "oppai")
        await ctx.send(embed=img)

    @nsfw.command(name="oral")
    @is_nsfw()
    async def oral(self, ctx: Context):
        """Any kind of erotic content, basically any nsfw image."""
        img = await self._get_nsfw_image(ctx, "oral")
        await ctx.send(embed=img)

    @nsfw.command(name="paizuri")
    @is_nsfw()
    async def paizuri(self, ctx: Context):
        """A category of hentai that involves breast sex, also known as titty fucking."""
        img = await self._get_nsfw_image(ctx, "paizuri")
        await ctx.send(embed=img)

    @nsfw.command(name="selfie", aliases=("selfies",))
    @is_nsfw()
    async def selfie(self, ctx: Context):
        """A girl taking a lewd picture of herself."""
        img = await self._get_nsfw_image(ctx, "selfies")
        await ctx.send(embed=img)

    @nsfw.command(name="uniform")
    @is_nsfw()
    async def uniform(self, ctx: Context):
        """Girls wearing any kind of uniform."""
        img = await self._get_nsfw_image(ctx, "uniform")
        await ctx.send(embed=img)

    @nsfw.command(name="ecchi")
    @is_nsfw()
    async def ecchi(self, ctx: Context):
        """Slightly explicit sexual content."""
        img = await self._get_nsfw_image(ctx, "ecchi")
        await ctx.send(embed=img)

    @command(name="waifu")
    async def waifu(self, ctx: Context):
        img = await self._get_sfw_image(ctx, "waifu")
        await ctx.send(embed=img)


async def setup(bot: Bot):
    await bot.add_cog(NSFW(bot))
