import discord

from .constants import GREEN_EMBED_COLOR, RED_EMBED_COLOR


def create_embed_failure(message: str) -> discord.Embed:
    return discord.Embed(color=RED_EMBED_COLOR).add_field(name="", value=message)


def create_embed_success(message: str) -> discord.Embed:
    return discord.Embed(color=GREEN_EMBED_COLOR).add_field(name="", value=message)
