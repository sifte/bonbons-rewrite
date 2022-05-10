from random import choice

from discord.ext.tasks import loop
from discord.ext.commands import Cog

class Tasks(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.names = ['sexy-general', 'soothing-general', 'hot-general', 'geneeral', 'neralgen', 'acey-is-sexy', 'dead-general', 'active-general']
		self.edit_general_chat.start()
		
	@loop(minutes=6)
	async def edit_general_chat(self):
		channel = self.bot.get_channel(880387280576061450) or await self.bot.fetch_channel(880387280576061450)
		await channel.edit(name=choice(self.names))
		
async def setup(cx):
	await cx.add_cog(Tasks(cx))
