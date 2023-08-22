import json
import logging
import os
from io import BytesIO
from tempfile import TemporaryDirectory

import discord
import replicate
from discord.ext import commands

from millenia import Millenia
from utils.context import Context
from utils.DiscordImageSaver import DiscordImageSaver
from utils.embed import create_embed_failure, create_embed_success

_logger = logging.getLogger(__name__)

class UpScalerCog(commands.Cog):
    def __init__(self, bot: Millenia):
        self.bot = bot

    

    @commands.command()
    async def upscale (self, ctx: Context, image: discord.Attachment):
        """Upscale and clean up an image.
        \n
        This image must be downloaded to use in the api as a path, as the api cannot handle image url links, or buffers
        \n
        The downloaded image will be promptly deleted after being sent in `Context`

        Parameters
        ----------
        ctx : `Context`
            The command's context
        """
        
        image_provided_embed = create_embed_success(message="Output image loading, this may take up to 20 seconds")

        await ctx.send(embed=image_provided_embed)

        buffer = BytesIO(await image.read())

        output_image = replicate.run(
            "nightmareai/real-esrgan:42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b", 
            input={
                "image": buffer
            }
        )
        await ctx.send(f"{output_image}")

        #os.remove(f"{path}")

async def setup(bot: Millenia):
    _logger.info("Loading cog ToDoCog")
    await bot.add_cog(UpScalerCog(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog UpScalerCog")