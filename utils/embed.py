from typing import Literal, Optional

import discord

from .constants import GREEN_EMBED_COLOR, RED_EMBED_COLOR


def create_embed_failure(message: str, color: Optional[int] | None = RED_EMBED_COLOR) -> discord.Embed:
    """
    Creates a VERY minimal embed with preset color parameters.

    ----------
    Parameters
    ----------
    message: str

    color: Defaults to Light Red
    """
    return discord.Embed(color=color).add_field(name="", value=message)


def create_embed_success(message: str, color: Optional[int] | None = GREEN_EMBED_COLOR) -> discord.Embed:
    """
    Creates a VERY minimal embed with preset color parameters.

    ----------
    Parameters
    ----------
    message: str

    color: Defaults to Light Green
    """
    return discord.Embed(color=color).add_field(name="", value=message)
