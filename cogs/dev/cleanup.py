import datetime
import logging
from datetime import timezone
from typing import Optional

import discord
from discord.ext import commands

from millenia import Millenia
from utils.context import GuildContext
from utils.embed import create_embed_failure, create_embed_success

_logger = logging.getLogger(__name__)


class Cleanup(commands.Cog):
    def __init__(self, bot: Millenia):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def cleanup(self, ctx: GuildContext, limit: int | None = 25):
        """Deletes any messages sent by the bot, or message starting with the bot prefix.

        Parameters
        ----------
        limit : Optional[int] | None, optional
            the amount of message you want to delete, by default 25
        """

        deleted = await ctx.channel.purge(
            check=lambda m: m.author == self.bot.user or m.content.startswith("aml"), limit=limit
        )

        messages_deleted_embed = create_embed_success(message=f"Deleted {len(deleted)} messages")

        await ctx.send(embed=messages_deleted_embed)


async def setup(bot: Millenia):
    _logger.info("Loading cog Cleanup")
    await bot.add_cog(Cleanup(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog Cleanup")
