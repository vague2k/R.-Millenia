import logging
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import find

from millenia import Millenia

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
            has_role_embed = discord.Embed(title="", description="", color=0xD97373)
            has_role_embed.add_field(
                name="",
                value="It looks like you already have this pronoun as a role.\nIf you would like to remove it, please use `/pronoun <remove>`.",
            )
            await interaction.response.send_message(embed=has_role_embed, delete_after=60)

        else:
            added_embed = discord.Embed(title="", description="", color=0xB2D973)
            added_embed.add_field(name="", value=f"The role you chose, **{role}** has been added,\nEnjoy!")
            await member.add_roles(role)  # type: ignore
            await interaction.response.send_message(embed=added_embed, delete_after=60)

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
            never_had_embed = discord.Embed(title="", description="", color=0xD97373)
            never_had_embed.add_field(
                name="",
                value="It looks like this role was either never given or already removed.\nIf you would like to add it, please use `/pronoun <give>`.",
            )
            await interaction.response.send_message(embed=never_had_embed, delete_after=60)

        else:
            removed_embed = discord.Embed(title="", description="", color=0xB2D973)
            removed_embed.add_field(name="", value=f"The role you chose, **{role}** has been removed,\nEnjoy!")
            await member.remove_roles(role)  # type: ignore
            await interaction.response.send_message(embed=removed_embed, delete_after=60)


async def setup(bot: Millenia):
    _logger.info("Loading cog pronoun")
    await bot.add_cog(PronounGroup(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog pronoun")
