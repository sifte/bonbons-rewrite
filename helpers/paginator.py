import discord
from discord.ext import commands

BUTTON_ROW = 1


class Paginator(discord.ui.View):
    def __init__(
        self,
        ctx: commands.Context,
        messages: list,
        *,
        embed: bool = False,
        timeout: int = 120,
    ):
        super().__init__(timeout=timeout)
        self.messages = messages
        self.embed = embed
        self.current_page = 0
        self.ctx = ctx

    async def on_timeout(self) -> None:
        await self.msg.edit(view=None)

    async def interaction_check(self, inter) -> bool:
        if inter.user.id != self.ctx.author.id:
            await inter.response.send_message(
                f"You are not the owner of this message.",
                ephemeral=True,
            )
            return False
        return True

    async def show_page(self, inter, page: int):
        if page >= len(self.messages):
            self.current_page = 0
        else:
            self.current_page = page

        data = self.messages[self.current_page]

        if self.embed:
            await inter.edit_original_message(embed=data, view=self)
        if not self.embed:
            await inter.edit_original_message(content=data, view=self)

    @discord.ui.button(label="<<", style=discord.ButtonStyle.grey)
    async def back_two(self, inter, button: discord.ui.Button):
        await inter.response.defer()
        await self.show_page(inter, self.current_page - self.current_page)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple)
    async def back_one(self, inter, button: discord.ui.Button):
        await inter.response.defer()
        await self.show_page(inter, self.current_page - 1)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next_one(self, inter, button: discord.ui.Button):
        await inter.response.defer()
        await self.show_page(inter, self.current_page + 1)

    @discord.ui.button(label="️>>", style=discord.ButtonStyle.grey)
    async def next_two(self, inter, button: discord.ui.Button):
        await inter.response.defer()
        await self.show_page(inter, self.current_page - self.current_page - 1)


class HelpMenuPaginator(discord.ui.View):
    def __init__(
        self,
        ctx: commands.Context,
        messages: list,
        *,
        embed: bool = False,
        timeout: int = 120,
    ):
        super().__init__(timeout=timeout)
        self.messages = messages
        self.embed = embed
        self.current_page = 0
        self.ctx = ctx

    async def on_timeout(self) -> None:
        await self.msg.edit(view=None)

    async def interaction_check(self, inter) -> bool:
        if inter.user.id != self.ctx.author.id:
            await inter.response.send_message(
                f"You are not the owner of this message.",
                ephemeral=True,
            )
            return False
        return True

    async def show_page(self, inter, page: int):
        if page >= len(self.messages):
            self.current_page = 0
        else:
            self.current_page = page

        data = self.messages[self.current_page]

        if self.embed:
            await inter.edit_original_message(embed=data, view=self)
        if not self.embed:
            await inter.edit_original_message(content=data, view=self)

    @discord.ui.button(label="<<", style=discord.ButtonStyle.grey, row=BUTTON_ROW)
    async def back_two(self, inter, button: discord.ui.Button):
        await inter.response.defer()
        await self.show_page(inter, self.current_page - self.current_page)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple, row=BUTTON_ROW)
    async def back_one(self, inter, button: discord.ui.Button):
        await inter.response.defer()
        await self.show_page(inter, self.current_page - 1)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, row=BUTTON_ROW)
    async def next_one(self, inter, button: discord.ui.Button):
        await inter.response.defer()
        await self.show_page(inter, self.current_page + 1)

    @discord.ui.button(label="️>>", style=discord.ButtonStyle.grey, row=BUTTON_ROW)
    async def next_two(self, inter, button: discord.ui.Button):
        await inter.response.defer()
        await self.show_page(inter, self.current_page - self.current_page - 1)
