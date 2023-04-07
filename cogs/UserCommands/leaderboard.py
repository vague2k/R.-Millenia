#
# How I usually lay out an extension, feel free to use it if you want, or don't
#
import logging

import discord
from discord.ext import commands
from discord import app_commands

from millenia import Millenia

_logger = logging.getLogger(__name__)

@app_commands.guild_only()
class Leaderboard(commands.GroupCog, group_name = "leaderboard"):
    def __init__(self, bot: Millenia):
        self.bot = bot

    @app_commands.command(name="pronoun", description="hmm... who keeps removing their pronouns?")
    async def pronoun_remove_leaderboard(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong")

async def setup(bot: Millenia):
    _logger.info("Loading cog Leaderboard")
    await bot.add_cog(Leaderboard(bot))

async def teardown(_: Millenia):
    _logger.info("Unloading cog Leaderboard")