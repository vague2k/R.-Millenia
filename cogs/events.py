#
# How I usually lay out an extension, feel free to use it if you want, or don't
#
import logging
import discord
from discord.ext import commands
import asqlite


from millenia import Millenia

_logger = logging.getLogger(__name__)


class Events(commands.Cog):
    def __init__(self, bot: Millenia):
        self.bot = bot

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command: discord.app_commands.Command):
        assert interaction.guild is not None
        member = interaction.user
        guild = interaction.guild

        if member.id == 1070552265062109204 or command.name != "remove":
            return

        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""SELECT guild_id FROM removeLeaderboard """)
                await cursor.execute(
                    """
                        INSERT INTO removeLeaderboard(
                            server_id,
                            member_id,
                            count) 
                            VALUES (?, ?, 1)
                        ON CONFLICT (server_id, member_id) DO UPDATE SET count = removeLeaderboard.count + 1
                        """,
                    (guild.id, member.id),
                )
                await conn.commit()


async def setup(bot: Millenia):
    _logger.info("Loading cog Events")
    await bot.add_cog(Events(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog Events")
