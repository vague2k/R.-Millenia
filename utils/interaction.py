from __future__ import annotations

from typing import TYPE_CHECKING, Union

import discord

if TYPE_CHECKING:
    from millenia import Millenia


class Interaction(discord.Interaction):
    bot: Millenia

class GuildContextInteraction(Interaction):
    author: discord.Member
    guild: discord.Guild
    channel: Union[discord.VoiceChannel, discord.TextChannel, discord.Thread]
    me: discord.Member