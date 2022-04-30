from discord.ext.commands import Cog, command, Context

from helpers.bot import Bonbons

class Logging(Cog):
    def __init__(self, bot: Bonbons) -> None:
        self.bot = bot
        self._logs = self.ensure_logs()
        
    def ensure_logs(self) -> None:
        if not hasattr(self.bot, 'logs'):
            self.bot.logs = []
            
        return self.bot.logs

    @Cog.listener()
    async def on_command(self, ctx: Context):
        if ctx.guild:
            log = f'[COMMAND] Command `{ctx.command.name}` ran in `{ctx.guild.name}/{ctx.channel.name}` (`{ctx.guild.id}`/`{ctx.channel.id}`) at `{ctx.message.created_at}`'
            self.bot.logs.append(log)

async def setup(bot: Bonbons) -> None:
    print('Loaded: Logging')
    await bot.add_cog(Logging(bot))
