"""
My error handlers, if you want them, feel free to do whatever.
"""
import logging
import traceback

import discord
from discord import app_commands
from discord.ext import commands

from millenia import Millenia
from utils.context import Context

_logger = logging.getLogger(__name__)


class ErrorHandler(commands.Cog):
    def __init__(self, bot: Millenia) -> None:
        self.bot = bot

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            if interaction.response.is_done():
                await interaction.followup.send(f"A little too quick there, try again in {error.retry_after:,.1f} seconds.")
            else:
                await interaction.response.send_message(
                    f"A little too quick there, try again in {error.retry_after:,.1f} seconds."
                )

        else:
            trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            _logger.error("Ignoring exception in app command {}:".format(interaction.command))
            _logger.error(trace)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: commands.CommandError) -> None:
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, commands.NotOwner, commands.TooManyArguments)

        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f"{ctx.command} has been disabled.", ephemeral=True)

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.send(f"{ctx.command} can not be used in Private Messages.", ephemeral=True)
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"A little too quick there. Try again in {error.retry_after:,.1f} seconds.", delete_after=4.0, ephemeral=True
            )

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"You do not have permission to use that command.", ephemeral=True)

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"You must have missed an argument ({error.param.name}), please try again.",
                ephemeral=True,
                delete_after=30.0,
            )

        elif isinstance(error, commands.BotMissingPermissions):
            perm_strings = [perm.replace("_", " ").title() for perm in error.missing_permissions]
            try:
                await ctx.send(f"I am missing the permissions needed to run that command: {', '.join(perm_strings)}")
            except discord.Forbidden:
                _logger.info(
                    f"Missing permissions {', '.join(perm_strings)} to run command '{ctx.command.qualified_name if ctx.command else 'None'}' in channel_id={ctx.channel.id}"
                )

        elif isinstance(error, commands.UserNotFound):
            await ctx.send(f"Could not find user {error.argument}.")

        elif isinstance(error, commands.BadArgument):
            err_str = "\n\t - ".join(str(arg) for arg in error.args)
            await ctx.send(f"You provided invalid argument(s):\n\t - {err_str}")

        elif isinstance(error, commands.BadLiteralArgument):
            await ctx.send(f"Invalid literal given, valid options: {' '.join(error.literals)}")

        elif isinstance(error, commands.RangeError):
            await ctx.send(f"Invalid value (**{error.value}**) given.")

        elif isinstance(error, commands.BadUnionArgument):
            await ctx.send(f"Failed converting {error.param.name}")

        else:
            trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            _logger.error("Ignoring exception in command {}:".format(ctx.command))
            _logger.error(trace)


async def setup(bot: Millenia):
    _logger.info("Loading cog ErrorHandler")
    await bot.add_cog(ErrorHandler(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog ErrorHandler")
