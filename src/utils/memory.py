import sqlite3
from datetime import datetime
from sentence_transformers import SentenceTransformer
import numpy as np


class Memory:

    def __init__(self, db_path="memory.db"):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            input TEXT,
            response TEXT,
            timestamp TEXT,
            embedding BLOB
            )

        """
        )
        self.connection.commit()

    def search_memory(self, user_id, query, top_k=3) -> str:
        query_vec = self.embedder.encode(query)
        self.cursor.execute(
            "SELECT id, input, response, embedding FROM responses WHERE user_id = ?",
            (user_id,),
        )

        scored = []
        for row in self.cursor.fetchall():
            db_embedding = np.frombuffer(row[3], dtype=np.float32)
            similarity = np.dot(query_vec, db_embedding) / (
                np.linalg.norm(query_vec) * np.linalg.norm(db_embedding)
            )
            if similarity > 0.4:
                scored.append((similarity, row[1], row[2]))

        top_results = sorted(scored, reverse=True)[:top_k]
        memory = ""
        for result in top_results:
            memory += f"**{result[1]}**\n{result[2]}\n\n"
        return memory

    async def update_memory(self, user_id, input, response) -> None:
        embedding = self.embedder.encode(input + " " + response)

        self.cursor.execute(
            "INSERT INTO responses (user_id, input, response, embedding, timestamp) VALUES (?, ?, ?, ?, ?)",
            (
                user_id,
                input,
                response,
                embedding.tobytes(),
                datetime.now().isoformat(),
            ),
        )
        self.connection.commit()
