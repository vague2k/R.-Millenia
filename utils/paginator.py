"""
This is a super basic embed paginator, do whatever you want with it or just delete it idc.
"""
from collections import deque
from typing import List, Optional

import discord
from discord import ui


class BasicEmbedPaginator(ui.View):
    def __init__(self, *, pages: List[discord.Embed], timeout: Optional[float] = 180) -> None:
        super().__init__(timeout=timeout)

        if len(pages) == 0:
            raise ValueError("Cannot paginate a list without any items.")

        self.pages = deque(pages)

    async def update(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(embed=self.pages[0], view=self)

    @ui.button(label="<", style=discord.ButtonStyle.blurple)
    async def back_btn(self, interaction, _) -> None:
        self.pages.rotate(1)
        await self.update(interaction)

    @ui.button(label=">", style=discord.ButtonStyle.blurple)
    async def forward_btn(self, interaction, _) -> None:
        self.pages.rotate(-1)
        await self.update(interaction)
