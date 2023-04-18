from __future__ import annotations

import logging
from typing import List

import discord
from discord.ext import commands

from millenia import Millenia
from utils.constants import GREEN_EMBED_COLOR
from utils.context import GuildContext
from utils.dataclasses import TodoItem
from utils.embed import create_embed_failure, create_embed_success
from utils.paginator import BaseButtonPaginator

_logger = logging.getLogger(__name__)


class ToDoCog(commands.Cog):
    def __init__(self, bot: Millenia):
        self.bot = bot

    @commands.group()
    async def todo(self, ctx: GuildContext) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @todo.command(name="add")
    async def add_todo_item(self, ctx: GuildContext, *, content: str):
        """Add an item to your to-do list.

        Parameters
        ----------
        content : str
            The message you want to add to your to-do list.
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
            INSERT INTO todos(owner_id, guild_id, channel_id, message_id, content, added_at) VALUES (?, ?, ?, ?, ?, ?) RETURNING id""",
                owner_id,
                guild_id,
                channel_id,
                message_id,
                content,
                added_at,
            )
            await conn.commit()

        added_to_list_embed = create_embed_success(message=f"Added that to your list.")
        added_to_list_embed.set_footer(text=f"ID: {row['id']}")
        await ctx.send(embed=added_to_list_embed)

    @todo.command(name="list")
    async def list_all_todo_items(self, ctx: GuildContext):
        """List all your todo items"""

        async with self.bot.pool.acquire() as conn:
            results = await conn.fetchall(
                """SELECT * FROM todos WHERE owner_id = ? AND guild_id = ?""", ctx.author.id, ctx.guild.id
            )

        if not results:
            no_todos_embed = create_embed_failure(message="You don't seem to have any todos.")
            await ctx.send(embed=no_todos_embed)
            return

        entries = [TodoItem.from_row(row) for row in results]

        view = ThisPaginator(entries=entries, per_page=1, target=ctx)

        todo_embed = await view.embed()

        await ctx.send(embed=todo_embed, view=view)

    @todo.command(name="remove")
    async def remove_todo_item(self, ctx: GuildContext, item_id: int):
        """Remove an item from your to-do list using the item id.

        Parameters
        ----------
        item_id : int
            The id of the to-do list item.
        """
        async with self.bot.pool.acquire() as conn:
            row = await conn.fetchone(
                """DELETE FROM todos WHERE owner_id = ? AND guild_id = ? AND id = ? RETURNING *""",
                ctx.author.id,
                ctx.guild.id,
                item_id,
            )

            if row:
                remove_embed = create_embed_success(message=f"The item\n\n{row['content']}\n\nhas been removed.")
                await ctx.send(embed=remove_embed)
                return

            unable_to_remove_emebed = create_embed_failure(message=f"Unable to remove todo item with ID: {item_id}")
            await ctx.send(embed=unable_to_remove_emebed)


class ThisPaginator(BaseButtonPaginator[TodoItem, Millenia]):
    # The subclassed format page function that implements the logic of creating our embed.
    # You can do this however you please, but in this example we'll add a field for each item.
    async def format_page(self, entries: List[TodoItem], /) -> discord.Embed:
        """Formats the however you want the page of your embed to look

        Parameters
        ----------
        entries : List[TodoItem]
            The list of entries of your TodoItem class

        Returns
        -------
        discord.Embed
        """
        entry = entries[0]
        embed = discord.Embed(
            title="My todo list",
            description=f"[Jump!]({str(entry.added_message_jump_url)})",
            color=GREEN_EMBED_COLOR,
        )

        embed.add_field(name="", value=f"Item id: {entry.id}", inline=False)
        embed.add_field(name="", value=entry.content, inline=False)

        embed.set_footer(text="Page {0.current_page}/{0.total_pages}".format(self))
        return embed


async def setup(bot: Millenia):
    _logger.info("Loading cog ToDoCog")
    await bot.add_cog(ToDoCog(bot))


async def teardown(_: Millenia):
    _logger.info("Unloading cog ToDoCog")
