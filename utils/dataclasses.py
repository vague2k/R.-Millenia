from __future__ import annotations

import datetime
import sqlite3
from dataclasses import dataclass
from typing import NamedTuple


class PronounRemove_Entries(NamedTuple):
    server_id: int
    user_id: int
    count: int

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> PronounRemove_Entries:
        return cls(row["server_id"], row["user_id"], row["count"])


@dataclass(slots=True)
class TodoItem:
    id: int
    owner_id: int
    guild_id: int
    channel_id: int
    message_id: int
    content: str
    added_at: str  # ISO FORMAT DATETIME

    @classmethod
    def from_row(cls, row: sqlite3.Row, /) -> TodoItem:
        return cls(**dict(row))

    @property
    def added_at_dt(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.added_at)

    @property
    def added_message_jump_url(self) -> str:
        return f"https://discord.com/channels/{self.guild_id}/{self.channel_id}/{self.message_id}"
