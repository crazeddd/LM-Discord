import os, aiohttp, json
from typing import AsyncGenerator
from dotenv import load_dotenv

load_dotenv()


class LMStudioClient:

    def __init__(self):
        self.url = os.getenv("LM_STUDIO_URL", "localhost:1234")
        self.model = None

    async def initialize_model(self, model) -> None:

        if model is None:
            models = await self.get_models()
            if models and "data" in models and len(models["data"]) > 0:
                self.model = models["data"][0]["id"]
        else:
            self.model = model

    async def get_models(self) -> AsyncGenerator[dict, None]:
        url = f"{self.url}/v1/models"
        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as res:
                    if res.status == 200:
                        data = await res.json()
                        return data
                    else:
                        print("Error fetching models:", res.status)
                        return None
            except aiohttp.ClientError as e:
                print("Connection error:", e)
                return

    async def stream(self, prompt, system_prompt) -> AsyncGenerator[str, None]:
        url = f"{self.url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": True,
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=payload) as res:
                    async for line in res.content:
                        line = line.decode("utf-8").strip()

                        if not line.startswith("data:"):
                            continue

                        if line == "data: [DONE]":
                            break

                        try:
                            data = json.loads(line.replace("data: ", ""))
                            delta = data["choices"][0]["delta"]
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except Exception:
                            continue
            except aiohttp.ClientError as e:
                print("Connection error:", e)
                return
