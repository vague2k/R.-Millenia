import logging
from typing import Any, List

import discord
from discord.ext import commands

from millenia import Millenia
from utils.constants import GREEN_EMBED_COLOR
from utils.context import Context, GuildContext
from utils.dataclasses import TicketItem
from utils.embed import create_embed_failure, create_embed_success
from utils.paginator import BaseButtonPaginator

_logger = logging.getLogger(__name__)


class TicketSystem(commands.Cog):
    def __init__(self, bot: Millenia):
        self.bot = bot

    @commands.group()
    async def ticket(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @ticket.command()
    async def submit(self, ctx: GuildContext, *, content: str):
        """Submit a ticket for the bot dev to look at

        Parameters
        ----------
        content : str
            The submissions you would like to input
        """
        if not ctx.guild:
            return

        owner_id = ctx.author.id
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id
        message_id = ctx.message.id
        added_at = discord.utils.utcnow().isoformat()

        async with self.bot.pool.acquire() as conn:
            row = await conn.fetchone(
                """
            INSERT INTO tickets(owner_id, guild_id, channel_id, message_id, content, added_at) VALUES (?, ?, ?, ?, ?, ?) RETURNING id""",
                owner_id,
                guild_id,
                channel_id,
                message_id,
                content,
                added_at,
            )
            await conn.commit()

        ticket_submitted_embed = create_embed_success(message=f"Your ticket has been submitted.\nThank you!")
        ticket_submitted_embed.set_footer(text=f"Ticket ID: {row['id']}")
        await ctx.send(embed=ticket_submitted_embed)

    @ticket.command()
    async def check(self, ctx: GuildContext):
        """Check how many ticket submissions you made

        Parameters
        ----------
        ctx : GuildContext
        """
        async with self.bot.pool.acquire() as conn:
            results = await conn.fetchall("""SELECT * FROM tickets WHERE owner_id = ?""", ctx.author.id)

        if not results:
            no_todos_embed = create_embed_failure(message="You don't have any ticket submissions.")
            await ctx.send(embed=no_todos_embed)
            return

        entries = [TicketItem.from_row(row) for row in results]

        view = ThisPaginator(entries=entries, per_page=1, target=ctx)

        user_tickets = await view.embed()

        await ctx.send(embed=user_tickets, view=view)

    @ticket.command()
    @commands.is_owner()
    async def all(self, ctx: Context):
        """Check all the tickets submissions made by users accross all servers that the bot is in"""

        async with self.bot.pool.acquire() as conn:
            results = await conn.fetchall("""SELECT * FROM tickets""")

        if not results:
            no_tickets_embed = create_embed_failure(message="There are no tickets to see right now.")
            await ctx.send(embed=no_tickets_embed)
            return

        entries = [TicketItem.from_row(row) for row in results]

        view = BotOwnerPaginator(entries=entries, per_page=1, target=ctx)

        handle_tickets_embed = await view.embed()

        await ctx.send(embed=handle_tickets_embed, view=view)

    @ticket.command(hidden=True)
    @commands.is_owner()
    async def resolve(self, ctx: Context, item_id: int, comment: Any | None):
        """Mark a ticket as resolved. This will delete the ticket from the DB and send a confirmation to the user.

        Parameters
        ----------
        item_id : int
            The id of the ticket submission
        comment : Any | None
            A comment made by the bot dev, if none it will send "No comment given" to the user
        """
        if comment is None:
            comment = "No Comment Given"

        async with self.bot.pool.acquire() as conn:
            row = await conn.fetchone(
                """DELETE FROM tickets WHERE id = ? RETURNING *""",
                item_id,
            )
            await conn.commit()

            if row:
                ticket_owner_id = self.bot.get_user(row["owner_id"])

                remove_embed = discord.Embed(
                    title="You have marked this ticket submission as resolved",
                    description=row["content"],
                    color=GREEN_EMBED_COLOR,
                )
                remove_embed.add_field(name="Comment", value=comment)
                remove_embed.add_field(
                    name="",
                    value="The original user who submitted the ticket will be notified that it has been resolved",
                    inline=False,
                )
                remove_embed.set_footer(text=f"The following comment: {comment} will also be sent to them")
                await ctx.send(embed=remove_embed)

                if ticket_owner_id:
                    owner_ticket_resolved_embed = discord.Embed(
                        title=f"Hello {ticket_owner_id.name}, your ticket for me has been resolved.",
                        description=row["content"],
                        color=GREEN_EMBED_COLOR,
                    )
                    owner_ticket_resolved_embed.add_field(name="Comment", value=comment, inline=False)
                    owner_ticket_resolved_embed.add_field(name="Your ticket id was", value=item_id, inline=False)
                    owner_ticket_resolved_embed.set_footer(
                        text="Thank you for submitting a ticket! If there are any more problems, please submit another one."
                    )
                    await ticket_owner_id.send(embed=owner_ticket_resolved_embed)

                return

            unable_to_resolve_emebed = create_embed_failure(message=f"Unable to resolve ticket with invalid ID: {item_id}")
            await ctx.send(embed=unable_to_resolve_emebed)


class ThisPaginator(BaseButtonPaginator[TicketItem, Millenia]):
    async def format_page(self, entries: List[TicketItem], /) -> discord.Embed:
        """Formats the however you want the page of your embed to look

        Parameters
        ----------
        entries : List[TicketItem]
            The list of entries of your TicketItem class

        Returns
        -------
        discord.Embed
        """
        entry = entries[0]
        embed = discord.Embed(
            title="My Submitted Tickets",
            description=f"[Jump!]({str(entry.added_message_jump_url)})",
            color=GREEN_EMBED_COLOR,
        )

        embed.add_field(name="", value=f"Item id: {entry.id}", inline=False)
        embed.add_field(name="", value=entry.content, inline=False)

        embed.set_footer(text="Page {0.current_page}/{0.total_pages}".format(self))
        return embed


class BotOwnerPaginator(BaseButtonPaginator[TicketItem, Millenia]):
    async def format_page(self, entries: List[TicketItem], /) -> discord.Embed:
        """Formats the however you want the page of your embed to look

        Parameters
        ----------
        entries : List[TicketItem]
            The list of entries of your TicketItem class

        Returns
        -------
        discord.Embed
        """
        entry = entries[0]
        embed = discord.Embed(
            title="Submitted Tickets across all servers",
            description="",
            color=GREEN_EMBED_COLOR,
        )
        embed.add_field(name="Ticket Content", value=f"{entry.content}")
        embed.add_field(name="Ticket ID", value=f"{entry.id}", inline=False)
        embed.add_field(name="From Server", value=f"{self.bot.get_guild(entry.guild_id).name}")  # type: ignore
        embed.add_field(name="User who submitted ticket", value=f"{self.bot.get_user(entry.owner_id).name}#{self.bot.get_user(entry.owner_id).discriminator}")  # type: ignore
        embed.add_field(name="Server ID", value=entry.guild_id, inline=False)
        embed.add_field(name="User ID", value=entry.owner_id, inline=True)

        embed.set_footer(text="Page {0.current_page}/{0.total_pages}".format(self))
        return embed


async def setup(bot: Millenia):
    _logger.info("Loading cog Tickets")
    await bot.add_cog(TicketSystem(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog Tickets")
