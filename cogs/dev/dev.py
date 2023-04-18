from __future__ import annotations

import copy
import logging
from typing import Literal, Optional, Union

import discord
from discord.ext import commands

from millenia import Millenia
from utils.context import Context, GuildContext

_logger = logging.getLogger(__name__)


class Developer(commands.Cog):
    def __init__(self, bot: Millenia):
        self.bot = bot

    # Umbra's sync command, you probably know it.
    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        self, ctx: GuildContext, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None
    ) -> None:
        """Syncs command tree.

        Parameters
        -----------
        guilds: list[int]
            The guilds to sync to
        spec: str
            The spec to sync.
            ~ -> Current Guild
            * -> Globals to current guild
            ^ -> Clear globals copied to current guild.
        """
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()
            await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
            return
        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1
        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Allows you to delete any message your bot has sent by adding a wastebasket emoji to it."""
        WASTE_BASKET = "\U0001f5d1\U0000fe0f"

        if not await self.bot.is_owner(payload.member):  # type: ignore
            return

        if str(payload.emoji) != WASTE_BASKET:
            return

        message: discord.Message = discord.utils.get(
            self.bot.cached_messages, id=payload.message_id
        ) or await self.bot.get_channel(
            payload.channel_id
        ).fetch_message(  # type: ignore
            payload.message_id
        )

        if message.author.id == self.bot.user.id:  # type: ignore
            await message.delete()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sudo(
        self, ctx: Context, channel: Optional[discord.TextChannel], who: Union[discord.Member, discord.User], *, command: str
    ):
        """Run a command as another user optionally in another channel. This command respects checks and cooldowns.

        ex:
            - aml sudo #general @fretgfr sync ~
            - aml sudo @fretgfr sync ~
        """
        if not ctx.prefix:
            return
        msg = copy.copy(ctx.message)
        new_channel = channel or ctx.channel
        msg.channel = new_channel
        msg.author = who
        msg.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        await self.bot.invoke(new_ctx)

    @commands.command(hidden=True, name="sudo!")
    @commands.is_owner()
    async def override_sudo(
        self,
        ctx: Context,
        channel: Optional[discord.TextChannel],
        who: Optional[Union[discord.Member, discord.User]],
        *,
        command: str,
    ):
        """Run a command, bypassing checks and/or cooldowns, optionally in another channel, optionally as another person.

        ex:
            - aml sudo! #general @fretgfr sync ~
            - aml sudo! @fretgfr sync ~
            - aml sudo! sync ~      <----- This one runs it as you and allows you to bypass cooldowns on your own commands without a custom cooldown.
        """
        if not ctx.prefix:
            return
        msg = copy.copy(ctx.message)
        new_channel = channel or ctx.channel
        msg.channel = new_channel
        msg.author = who or ctx.author
        msg.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        await new_ctx.reinvoke()


async def setup(bot: Millenia):
    _logger.info("Loading cog Developer")
    await bot.add_cog(Developer(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog Developer")
