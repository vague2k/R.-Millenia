from __future__ import annotations

import asyncio
import datetime
import os
import pathlib
from typing import Union

import asqlite
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.context import Context

load_dotenv()

DB_FILENAME = "millenia.sqlite"
COMMAND_PREFIX = "m."  # Probably want to change this
INTENTS = discord.Intents.all()  # probably want to change this too.
TOKEN = str(os.getenv("DISCORD_BOT_TOKEN"))  # however you want to get this, probably reading it in from somewhere


class Millenia(commands.Bot):
    STARTED_AT: datetime.datetime

    def __init__(self, command_prefix, pool: asqlite.Pool, **options) -> None:
        super().__init__(command_prefix=command_prefix, **options)
        self.pool = pool
        self.STARTED_AT = discord.utils.utcnow()

    async def setup_hook(self) -> None:
        # Load jishasku, allows you to a lot of cool stuff from your bot
        # https://github.com/Gorialis/jishaku
        # You might want to change some of the settings, but those are the ones I use...
        await self.load_extension("jishaku")
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
        os.environ["JISHAKU_HIDE"] = "True"

        # This is an Umbra moment, loads anything in the cogs folder that doesn't start with an _
        for file in sorted(pathlib.Path("cogs").glob("**/[!_]*.py")):
            ext = ".".join(file.parts).removesuffix(".py")
            await self.load_extension(ext)

    async def on_message_edit(self, _: discord.Message, after: discord.Message) -> None:
        """Allow editing messages to rerun commands."""
        await self.process_commands(after)

    async def get_context(self, origin: Union[discord.Interaction, discord.Message], /, *, cls=Context) -> Context:
        return await super().get_context(origin, cls=cls)


async def main():

    discord.utils.setup_logging()  # Could change this out for however you want logging to be setup

    async with (
        asqlite.create_pool(DB_FILENAME) as pool,
        Millenia(command_prefix=COMMAND_PREFIX, pool=pool, intents=INTENTS) as bot
    ):
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
