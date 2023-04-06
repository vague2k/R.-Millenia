import logging
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import find

from millenia import Millenia
from utils.context import GuildContext

_logger = logging.getLogger(__name__)


@app_commands.guild_only()
class PronounGroup(commands.GroupCog, group_name="pronoun"):
    def __init__(self, bot: Millenia):
        self.bot = bot

    @app_commands.command(name="give", description="Give your self a pronoun as a role")
    @app_commands.describe(pronouns="Here's a list of pronouns your currently allowed to choose from")
    async def give_pronoun_role(
        self, interaction: discord.Interaction, pronouns: Literal["he/him", "she/her", "they/them", "it/its", "any pronouns"]
    ):
        member = interaction.user

        assert interaction.guild is not None
        role: discord.Role | None = find(lambda x: x.name.lower() == pronouns, interaction.guild.roles)
        if role is None:
            role = await interaction.guild.create_role(name=pronouns, mentionable=False)

        if role in member.roles:  # type: ignore
            await interaction.response.send_message(
                "It looks like you already have this pronoun as a role. If you would like to remove it, please use `m.pronoun remove`.",
                ephemeral=True,
            )

        else:
            await member.add_roles(role)  # type: ignore
            await interaction.response.send_message(f"The role you chose, **{role}** has been added, Enjoy!", ephemeral=True)

    @app_commands.command(name="remove", description="Remove a pronoun role from your roles")
    @app_commands.describe(remove="Here's a list of pronouns your currently allowed to choose from")
    async def change_pronoun_role(
        self, interaction: discord.Interaction, remove: Literal["he/him", "she/her", "they/them", "it/its", "any pronouns"]
    ):
        member = interaction.user

        assert interaction.guild is not None
        role: discord.Role | None = find(lambda x: x.name.lower() == remove, interaction.guild.roles)

        """This "If role is none statement" is purely for an edge case"""
        if role is None:
            role = await interaction.guild.create_role(name=remove, mentionable=False)

        if role not in member.roles:  # type: ignore
            await interaction.response.send_message(
                "It looks like this role was either never given or already removed. If you would like to add it, please use `m.pronoun give`.",
                ephemeral=True,
            )

        else:
            await member.remove_roles(role)  # type: ignore
            await interaction.response.send_message(
                f"The role you chose, **{role}** has been removed, Enjoy!", ephemeral=True
            )


async def setup(bot: Millenia):
    _logger.info("Loading cog pronoun")
    await bot.add_cog(PronounGroup(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog pronoun")
