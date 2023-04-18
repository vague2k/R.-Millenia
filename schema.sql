CREATE TABLE if not EXISTS removeLeaderboard(
    server_id INTERGER,
    user_id INTEGER,
    count INTEGER,
    PRIMARY KEY(server_id, user_id)
);

CREATE TABLE if not EXISTS todos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    added_at TEXT NOT NULL
);
CREATE TABLE if not EXISTS tickets(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    added_at TEXT NOT NULL
);
