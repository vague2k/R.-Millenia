from __future__ import annotations

import asyncio
import datetime
import os
import pathlib
import sys
from typing import Union

import asqlite
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.context import Context

load_dotenv()

TESTING = sys.platform == "win32"

DB_FILENAME = "millenia.sqlite" if not TESTING else "test-millenia.sqlite"
COMMAND_PREFIX = "aml " if not TESTING else "amt "
INTENTS = discord.Intents.all()
TOKEN = str(os.getenv("DISCORD_BOT_TOKEN")) if not TESTING else str(os.getenv("TEST_BOT_TOKEN"))


class Millenia(commands.Bot):
    STARTED_AT: datetime.datetime

    def __init__(self, command_prefix, pool: asqlite.Pool, **options) -> None:
        super().__init__(command_prefix=command_prefix, **options)
        self.pool = pool
        self.STARTED_AT = discord.utils.utcnow()

    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
        os.environ["JISHAKU_HIDE"] = "True"

        with open("schema.sql", "r") as file:
            schema = file.read()

        async with self.pool.acquire() as conn:
            await conn.executescript(schema)

        # Loads anything in the cogs folder that doesn't start with an _
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
        Millenia(command_prefix=COMMAND_PREFIX, pool=pool, intents=INTENTS) as bot,
    ):
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
