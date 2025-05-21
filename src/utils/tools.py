from duckduckgo_search import DDGS
from utils.lmstudio_client import LMStudioClient


class Tools:

    def __init__(self):
        self.lm_studio = LMStudioClient()

    async def web_search(self, prompt, max_results=2):
        system_prompt = """
    You are helping decide whether a user's message requires a web search.

    IMPORTANT:
    - If the question mentions current events, public figures, politics, the economy, recent data, live events, or anything time-sensitive, assume a search *is needed*.
    - Only respond with "No search needed" if the question is timeless (e.g. basic math, historical facts before 2024 or fictional lore).
    - If the question *definitely* needs a search, rewrite it as a short search query.
    """

        query = ""

        async for token in self.lm_studio.stream(prompt + "/no_think", system_prompt):
            if token.strip() == "EOF:":
                break
            query += token

        print(query)
        if "no search needed" in query.lower():
            return "No search needed."
        else:
            try:
                with DDGS() as ddgs:
                    results = ddgs.text(query, max_results=max_results)
                    print("Search results:", results)
                    if not results:
                        return "No search results found, inform user of this."
                    return [f"{r['title']}: {r['body']}" for r in results]
            except Exception as e:
                print("Search error:", e)
                return "Search failed, inform user of failure."
