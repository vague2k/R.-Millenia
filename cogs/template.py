#
# How I usually lay out an extension, feel free to use it if you want, or don't
#
import logging

from discord.ext import commands

from millenia import Millenia

_logger = logging.getLogger(__name__)

class SampleCog(commands.Cog):
    def __init__(self, bot: Millenia):
        self.bot = bot

    # Content goes here

async def setup(bot: Millenia):
    _logger.info("Loading cog SampleCog")
    await bot.add_cog(SampleCog(bot))

async def teardown(_: Millenia):
    _logger.info("Unloading cog SampleCog")
