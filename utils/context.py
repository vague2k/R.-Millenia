"""
The subclasses contained in here should be used instead of the normal commands.Context.
GuildContext is useful for guild_only commands.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Union

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from millenia import Millenia


class Context(commands.Context):
    bot: Millenia


class GuildContext(Context):
    author: discord.Member
    guild: discord.Guild
    channel: Union[discord.VoiceChannel, discord.TextChannel, discord.Thread]
    me: discord.Member
