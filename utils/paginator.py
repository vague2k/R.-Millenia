from __future__ import annotations

import abc
from typing import Generic, List, Optional, Union

import discord
from discord.ext import commands
from typing_extensions import Self, TypeAlias, TypeVar

from utils.embed import create_embed_failure

T = TypeVar("T")
BotT = TypeVar("BotT", bound="commands.Bot", default="commands.Bot")
TargetType: TypeAlias = Union["discord.Interaction[BotT]", "commands.Context[BotT]"]


class BaseButtonPaginator(Generic[T, BotT], discord.ui.View, abc.ABC):
    """The base implementation of a button paginator. This class should be inherited
    then the custom instance defined.

    Parameters
    ----------
    entries: List[Any]
        The entries to paginate.
    per_page: int
        The amount of entries to show per page.
    clamp_pages: bool
        Whether to clamp the pages to the max and min page. This means that when the user
        reaches the max page, it will go back to the first page. Likewise, when the user
        reaches the first page, it will go back to the last page.
    target: Optional[Union[:class:`discord.Interaction`, :class:`commands.Context`]]
        The target interaction or context to use for the paginator. This is used to
        ensure that the user invoking the paginator is the same user that is interacting
        with the paginator.
        If this is ``None`` then the interaction check will always return True.
    """

    def __init__(
        self, *, entries: List[T], per_page: int = 6, clamp_pages: bool = True, target: Optional[TargetType[BotT]] = None
    ) -> None:
        super().__init__(timeout=180)
        self.entries: List[T] = entries
        self.per_page: int = per_page
        self.clamp_pages: bool = clamp_pages

        self.target: Optional[TargetType[BotT]] = target
        self.author: Optional[Union[discord.User, discord.Member]] = target and (
            target.user if isinstance(target, discord.Interaction) else target.author
        )

        self._current_page_index = 0
        self.pages = [entries[i : i + per_page] for i in range(0, len(entries), per_page)]

    @property
    def max_page(self) -> int:
        """:class:`int`: The max page count for this paginator."""
        return len(self.pages)

    @property
    def min_page(self) -> int:
        """:class:`int`: The min page count for this paginator."""
        return 1

    @property
    def current_page(self) -> int:
        """:class:`int`: The current page the user is on."""
        return self._current_page_index + 1

    @property
    def total_pages(self) -> int:
        """:class:`int`: Returns the total amount of pages."""
        return len(self.pages)

    @abc.abstractmethod
    def format_page(self, entries: List[T], /) -> discord.Embed:
        """|maybecoro|
        Used to make the embed that the user sees. This can be a coroutine or a regular
        function. This must be overwritten by the subclass.
        Parameters
        ----------
        entries: List[Any]
            A list of entries for the current page.
        Returns
        -------
        :class:`discord.Embed`
            The embed for this page.
        """
        raise NotImplementedError("Subclass did not overwrite format_page coro.")

    async def embed(self) -> discord.Embed:
        """|coro|
        A helper function to get the embed for the current page.
        Returns
        -------
        :class:`discord.Embed`
            The embed for the current page.
        """
        return await discord.utils.maybe_coroutine(self.format_page, self.pages[self._current_page_index])

    async def interaction_check(self, interaction: discord.Interaction[BotT], /) -> Optional[bool]:
        """|coro|
        The base interaction check for the given view.
        This will always return ``True`` if the target is ``None``, otherwise it will check
        that the user invoking the paginator is the same user that is interacting with the
        paginator.
        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction to check.
        Returns
        -------
        Optional[:class:`bool`]
            The result of the interaction check. If this returns ``None`` then the interaction
            was responded to with an error message to the user.
        """
        if self.target is None:
            return True

        assert self.author

        # Ensure this is the correct invoker
        if self.author.id != interaction.user.id:
            not_your_list_embed = create_embed_failure(message="This list isn't yours.")
            return await interaction.response.send_message(embed=not_your_list_embed, ephemeral=True)

        # Ensure they invoke it in the correct channel.
        if self.target.channel and interaction.channel and self.target.channel.id != interaction.channel.id:
            not_right_channel_embed = create_embed_failure("This isn't in the right channel.")
            return await interaction.response.send_message(embed=not_right_channel_embed, ephemeral=True)

        return True

    def _switch_page(self, count: int, /) -> None:
        self._current_page_index += count

        if self.clamp_pages:
            if count < 0:  # Going down
                if self._current_page_index < 0:
                    self._current_page_index = self.max_page - 1
            elif count > 0:  # Going up
                if self._current_page_index > self.max_page - 1:  # - 1 for indexing
                    self._current_page_index = 0

        return

    @discord.ui.button(emoji="\U000025c0", style=discord.ButtonStyle.blurple)
    async def on_arrow_backward(
        self, interaction: discord.Interaction[BotT], button: discord.ui.Button[Self]
    ) -> discord.InteractionMessage:
        """|coro|
        The button to represent going backwards a page.
        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction created from the user invoking the button.
        button: :class:`discord.ui.Button`
            The button that was pressed.
        """
        await interaction.response.defer()

        self._switch_page(-1)

        embed = await self.embed()
        return await interaction.edit_original_response(embed=embed)

    @discord.ui.button(emoji="\U000025b6", style=discord.ButtonStyle.blurple)
    async def on_arrow_forward(
        self, interaction: discord.Interaction[BotT], button: discord.ui.Button[Self]
    ) -> discord.InteractionMessage:
        """|coro|
        The button to represent going forward a page.
        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction created from the user invoking the button.
        button: :class:`discord.ui.Button`
            The button that was pressed.
        """
        await interaction.response.defer()

        self._switch_page(1)

        embed = await self.embed()
        return await interaction.edit_original_response(embed=embed)

    @discord.ui.button(emoji="\U000023f9", style=discord.ButtonStyle.blurple)
    async def on_stop(
        self, interaction: discord.Interaction[BotT], button: discord.ui.Button[Self]
    ) -> discord.InteractionMessage:
        """|coro|
        The button to represent stopping the paginator. This will disable all children
        to the view then edit the original message with the updated view.
        This will also call :meth:`~discord.ui.View.stop` to stop the view.
        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction created from the user invoking the button.
        button: :class:`discord.ui.Button`
            The button that was pressed.
        """
        await interaction.response.defer()

        for child in self.children:
            child.disabled = True  # type: ignore

        self.stop()

        return await interaction.edit_original_response(view=self)
