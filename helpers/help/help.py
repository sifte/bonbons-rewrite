from typing import Mapping, Optional
from textwrap import dedent
import discord
from discord import Color, Embed
from discord.ext.commands import Cog, Command, Group, HelpCommand

from helpers.paginator import Paginator

from .views import HelpCommandMenu


class CustomHelpCommand(HelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs={
                "hidden": True,
                "help": "Shows help about a category, group, or a command.",
            }
        )

    async def send(self, **kwargs):
        return await self.get_destination().send(**kwargs)

    async def send_bot_help(
        self, mapping: Mapping[Optional[Cog], list[Command]]
    ) -> None:

        description = f"""
        Hello! I am bonbons, I was made by sift#0410 around <t:1631859987:R>.
        Use the dropdown below to navigate through my modules. If you need help with a specific command, use `{self.context.clean_prefix}help [command]`.
        """

        embed = Embed(
            title="Help Menu",
            description=dedent(description),
            color=Color.og_blurple(),
        )
        view = HelpCommandMenu(self.context, embed)

        view.msg = await self.send(
            embed=embed,
            view=view,
        )

    async def paginate(
        self, title: str, description: str, commands, *, per_page: int
    ) -> None:
        embeds = []

        for number in range(0, len(commands), per_page):
            embed = discord.Embed(
                title=title,
                description=description,
                colour=discord.Color.og_blurple(),
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

        view = Paginator(self.context, embeds, embed=True)

        view.msg = await self.send(embed=embeds[0], view=view)

    async def send_help_embed(
        self,
        title: str,
        description: str,
        commands,
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

        await self.paginate(
            title, description, initial_commands, per_page=7
        )

    async def send_group_help(self, group: Group) -> None:
        await self.send_help_embed("Group Help", group.description, group.commands)

    async def send_cog_help(self, cog: Group) -> None:
        await self.send_help_embed(
            "Category Help",
            cog.description,
            cog.walk_commands(),
        )

    async def send_command_help(self, command: Command) -> None:
        embed = Embed(title="Command Help", color=Color.og_blurple())
        description = command.description or command.help or "..."

        embed.description = (
            f"```\n{command.qualified_name} {command.signature}\n```\n{description}"
        )

        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases))

        await self.send(embed=embed)
