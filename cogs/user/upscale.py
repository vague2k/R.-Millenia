import logging
import os
from typing import Optional

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
    async def upscale (self, ctx: Context):
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
        message = ctx.message
        image = message.attachments[0].url
        no_image_embed = create_embed_failure(message="No image was provided")
        image_provided_embed = create_embed_success(message="Output image loading, this may take up to 20 seconds")

        if not image:
            await ctx.send(embed=no_image_embed)
            return

        if image:
            # This image must be downloaded to use in the api as a path, as the api cannot handle image url links, or buffers
            saved_image = DiscordImageSaver(image, ctx.author.id, "bucket/upscale_images")
            await saved_image.save_image_from_url()
            await ctx.send(embed=image_provided_embed)

            output_image = replicate.run(
                "nightmareai/real-esrgan:42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b", 
                input={
                    # the downloaded image path is then used here
                    "image": open(f"bucket/upscale_images/{saved_image.image_name}", "rb"),
                }
            )
            await ctx.send(f"{output_image}")

            os.remove(f"bucket/upscale_images/{saved_image.image_name}")

async def setup(bot: Millenia):
    _logger.info("Loading cog ToDoCog")
    await bot.add_cog(UpScalerCog(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog UpScalerCog")