from discord import Color, Embed, Interaction, SelectOption
from discord.ext.commands import Command, Context, Group
from discord.ui import Select, View

from helpers.bot import Bonbons
from helpers.paginator import HelpMenuPaginator

BUTTON_ROW = 1


class HelpCommandDropdown(Select):
    def __init__(self, ctx: Context, embed: Embed) -> None:
        super().__init__(
            placeholder="Select a category..",
            min_values=1,
            max_values=1,
            row=0,
        )
        self.ctx = ctx
        self.embed = embed
        self.add_options()

    def add_options(self) -> None:
        self.append_option(
            SelectOption(
                emoji="🏠", label="Home", description="Go back to the main help page."
            )
        )

        for cog in self.ctx.bot.cogs:

            cog = self.ctx.bot.get_cog(cog)

            if cog.qualified_name in self.ctx.bot.ignored_cogs:
                continue

            if hasattr(cog, "emoji"):
                self.append_option(
                    SelectOption(
                        emoji=cog.emoji,
                        label=cog.qualified_name,
                        description=cog.description,
                    )
                )
            else:
                self.append_option(
                    SelectOption(
                        label=cog.qualified_name,
                        description=cog.description,
                    )
                )

    def sort_commands(
        self,
        commands: list[Command],
    ) -> None:

        initial_commands = []

        for command in commands:
            if isinstance(command, Group):
                for subcommand in command.commands:
                    if subcommand.hidden or not subcommand.enabled:
                        continue

                    signature = subcommand.signature
                    name = subcommand.qualified_name
                    help = subcommand.description or subcommand.help or "No help found."

                    initial_commands.append(
                        (f"{name} {signature}", help)
                    )

            if command.parent or command.hidden or not command.enabled:
                continue

            signature = command.signature
            name = command.qualified_name
            help = command.description or command.help or "No help found."

            initial_commands.append((f"{name} {signature}", help))

        return initial_commands

    async def paginate(
        self,
        title: str,
        description: str,
        commands: list[Command],
        *,
        per_page: int,
        interaction: Interaction,
    ) -> None:
        embeds = []

        for number in range(0, len(commands), per_page):
            embed = Embed(
                title=title,
                description=description,
                colour=Color.og_blurple(),
            )
            for command in commands[number : number + per_page]:
                embed.add_field(
                    name=command[0],
                    value=command[1],
                    inline=False,
                )

            embeds.append(embed)

        for index, embed in enumerate(embeds):
            embed.title += f"Page {index+1}/{len(embeds)}"
            embed.set_footer(
                text=f"Use b!help [command] for more info on a command."  # unsure on how I would make the prefix dynamic
            )

        view = HelpMenuPaginator(self.ctx, embeds, embed=True)
        view.add_item(self)

        view.msg = await interaction.edit_original_message(
            content=None, embed=embeds[0], view=view
        )

    async def callback(self, interaction) -> None:

        await interaction.response.defer()

        if self.values[0] == "Home":
            return await interaction.edit_original_message(
                content=None, embed=self.embed
            )

        cog = self.ctx.bot.get_cog(self.values[0])

        await self.paginate(
            "Category Help",
            cog.description,
            self.sort_commands(cog.walk_commands()),
            per_page=7,
            interaction=interaction,
        )


class HelpCommandMenu(View):
    def __init__(self, ctx: Context, embed: Embed) -> None:
        super().__init__(timeout=None)
        self.add_item(HelpCommandDropdown(ctx, embed))
        self.ctx = ctx

    async def interaction_check(self, interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                f"You are not the owner of this message.",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self) -> None:
        await self.msg.edit(view=None)
