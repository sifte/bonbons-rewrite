from discord.ext.commands import Cog

from helpers.bot import Bonbons
from helpers.help.help import CustomHelpCommand


class Help(Cog):
    def __init__(self, bot: Bonbons) -> None:
        self.bot = bot
        self.bot.help_command = CustomHelpCommand()


async def setup(bot: Bonbons) -> None:
    print("Loaded: Help")
    await bot.add_cog(Help(bot))
