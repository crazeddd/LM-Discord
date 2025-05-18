from duckduckgo_search import DDGS

# WEB SEARCH


class Tools:

    async def web_search(prompt, max_results=2):
        system_prompt = """
    You are helping decide whether a user's message requires a web search.

    IMPORTANT:
    - Your internal knowledge only goes up to 2023. It may be outdated.
    - If the question mentions current events, public figures, politics, the economy, recent data, live events, or anything time-sensitive, assume a search *is needed*.
    - Err on the side of doing a search if you're unsure.
    - Only respond with "No search needed" if the question is timeless (e.g. basic math, historical facts before 2023, or fictional lore).
    - If the question *definitely* needs a search, rewrite it as a short search query.

    Examples:
    User: Who is the current president of the US?
    Output: current us president

    User: What's 2 + 2?
    Output: No search needed

    User: Did Elon Musk step down?
    Output: elon musk twitter ceo 2024

    User: Tell me about photosynthesis.
    Output: No search needed
    """

        query = ""

        async for token in stream(prompt + "/no_think", system_prompt):
            query += token

        print(query)
        if "no search needed" in query.lower():
            return ["No search needed"]
        else:
            try:
                with DDGS() as ddgs:
                    results = ddgs.text(query, max_results=max_results)
                    return [f"{r['title']}: {r['body']}" for r in results]
            except Exception as e:
                print("Search error:", e)
                return ["[Search failed]"]
