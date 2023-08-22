import logging
from io import StringIO
from typing import Any, List, Mapping, Optional

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Command

from millenia import Millenia
from utils.constants import GREEN_EMBED_COLOR

_logger = logging.getLogger(__name__)


class MilleniaHelp(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping: Mapping[Optional[Cog], List[Command[Any, ..., Any]]], /) -> None:
        destination = self.get_destination()

        help_embed = discord.Embed(
            title="Millenia Help Commands",
            description="Use `aml help [command]` for more info on a command.\nYou can also use `aml help [category]` for more info on a category.",
            color=GREEN_EMBED_COLOR,
        )
        help_embed.set_footer(text=f"Listed are the commands you can run")
        field_description = StringIO()

        for command in await self.filter_commands(self.context.bot.walk_commands()):
            field_description.write(f"\naml {command.qualified_name}")

        help_embed.add_field(name="Commands", value=field_description.getvalue())
        await destination.send(embed=help_embed)

    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page, color=GREEN_EMBED_COLOR)
            await destination.send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot: Millenia):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MilleniaHelp()
        bot.help_command.cog = self


async def setup(bot: Millenia):
    _logger.info("Loading cog HelpCog")
    await bot.add_cog(Help(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog HelpCog")
