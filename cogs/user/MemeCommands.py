import io
import logging

import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from millenia import Millenia
from utils.context import GuildContext

_logger = logging.getLogger(__name__)


class MemeCommands(commands.Cog):
    def __init__(self, bot: Millenia):
        self.bot = bot

    @app_commands.command(
        name="spongebob-scream", description="Generates a spongebob screaming meme with top and bottom text"
    )
    @app_commands.describe(top_text="Set top text of the meme, up to 33 char")
    @app_commands.describe(bottom_text="Set bottom text of the meme, up to 33 char")
    async def generate_spongebob_meme(self, interaction: discord.Interaction, top_text: str, bottom_text: str):
        img = Image.open("./assets/spgbob_screaming.jpg")
        buff = io.BytesIO()

        font = ImageFont.truetype(font="./assets/impact.ttf", size=80)
        draw = ImageDraw.Draw(img)

        top_text = top_text.upper()
        bottom_text = bottom_text.upper()

        draw.text(xy=(570, 60), anchor="mm", text=top_text, font=font, stroke_width=3, stroke_fill=(0, 0, 0))
        draw.text(xy=(570, 1060), anchor="mm", text=bottom_text, font=font, stroke_width=3, stroke_fill=(0, 0, 0))

        img.save(buff, format="jpeg")
        buff.seek(0)
        await interaction.response.send_message(file=discord.File(buff, "spg-screaming.jpeg"))

    @commands.command(name="flmancode")
    @commands.guild_only()
    async def florida_man_code(self, ctx: GuildContext):
        file = discord.File("assets/florida_man_code.png")

        await ctx.send(file=file)


async def setup(bot: Millenia):
    _logger.info("Loading cog MemeCommands")
    await bot.add_cog(MemeCommands(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog MemeCommands")
