import sqlite3

connect = sqlite3.connect("memory.db")
cursor = connect.cursor()

class Memory:

    def __init__():
        cursor.execute(
            """
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        channel_id TEXT,
        role TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
        )
        connect.commit()

    def store_message(user_id, channel_id, role, content):
        cursor.execute(
            "INSERT INTO memory (user_id, channel_id, role, content) VALUES (?, ?, ?, ?)",
            (user_id, channel_id, role, content),
        )
        connect.commit()

    def get_memory_chunk(channel_id, limit):
        cursor.execute(
            """
            SELECT role, content FROM memory
            WHERE channel_id = ?
            ORDER BY timestamp DESC 
            LIMIT ?   
        """,
            (channel_id, limit),
        )
        rows = cursor.fetchall()[::-1]

        return "\n".join(f"{role}: {content}" for role, content in rows)
