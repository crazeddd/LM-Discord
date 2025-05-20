import sqlite3

from utils.lmstudio_client import LMStudioClient


class Memory:

    def __init__(self, db_path="memory.db"):
        self.lm_client = LMStudioClient()
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        
        self.cursor.execute(
            """
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        role TEXT,
        content TEXT
    )
    """
        )
        self.connection.commit()

    def get_memory(self, user_id):
        self.cursor.execute(
            """
            SELECT content FROM memory 
            WHERE user_id = ? 
            ORDER BY id DESC LIMIT 1
        """,
            (user_id,),
        )
        row = self.cursor.fetchone()

        return row[0] if row else "No memory yet."

    async def update_memory(self, user_id, role, messages):
        self.lm_studio = LMStudioClient()
        memory = self.get_memory(user_id)
        updated_memory = ""

        system_prompt = f"""
        Summarize the recent messages from {user_id} in a concise manner to be stored as memory.
        The memory is as follows:
        {memory}
        """

        async for token in self.lm_studio.stream(
            messages, system_prompt
        ):
            updated_memory += token

        self.cursor.execute(
            "INSERT INTO memory (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, updated_memory),
        )
        self.connection.commit()
