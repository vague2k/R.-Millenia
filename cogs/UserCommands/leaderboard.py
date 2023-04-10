import logging

import discord
from discord import app_commands
from discord.ext import commands

from millenia import Millenia
from utils.constants import GREEN_EMBED_COLOR
from utils.dataclasses import PronounRemove_Entries
from utils.embed import create_embed_failure

_logger = logging.getLogger(__name__)


@app_commands.guild_only()
class Leaderboard(commands.GroupCog, group_name="leaderboard"):
    def __init__(self, bot: Millenia):
        self.bot = bot

    @app_commands.command(name="pronoun", description="hmm... who keeps removing their pronouns?")
    async def pronoun_remove_leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()

        async with self.bot.pool.acquire() as conn:
            assert interaction.guild is not None

            results = await conn.fetchall(
                """
                SELECT * FROM removeLeaderboard 
                WHERE server_id = ? 
                ORDER BY count DESC 
                LIMIT 10
                """,
                (interaction.guild.id),
            )

        entries = [PronounRemove_Entries.from_row(row) for row in results]

        if not entries:
            no_entries_embed = create_embed_failure(message="There were no entries in my database for this server.")
            await interaction.followup.send(embed=no_entries_embed)
            return

        lead_embed = discord.Embed(title="Leaderboard", description="", color=GREEN_EMBED_COLOR)

        name_list = [(await self.bot.fetch_user(entry.user_id)).display_name for entry in entries]
        rank_list = [*range(1, len(name_list) + 1)]
        count_list = [entry.count for entry in entries]

        lead_embed.add_field(name="Rank", value="\n".join(str(rank) for rank in rank_list), inline=True)
        lead_embed.add_field(name="Name", value="\n".join(name for name in name_list), inline=True)
        lead_embed.add_field(name="Count", value="\n".join(str(count) for count in count_list), inline=True)

        await interaction.followup.send(embed=lead_embed)


async def setup(bot: Millenia):
    _logger.info("Loading cog Leaderboard")
    await bot.add_cog(Leaderboard(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog Leaderboard")
