import asyncio
import re
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lm_client = bot.lm_client
        self.memory = bot.memory
        self.tools = bot.tools
        self.local_memory = None

    async def get_channel_history(self, history) -> list:
        history = [msg async for msg in history]
        messages = []

        for msg in history:
            author_name = (
                msg.author.display_name
                if hasattr(msg.author, "display_name")
                else msg.author.name
            )

            content = msg.clean_content

            if self.bot and self.bot.user:
                bot_user = self.bot.user

                content = content.replace(f"<@{bot_user.id}>", "")
                content = content.replace(f"<@!{bot_user.id}>", "")

                bot_display = (
                    bot_user.display_name
                    if hasattr(bot_user, "display_name")
                    else bot_user.name
                )

                content = re.sub(
                    rf"@?{re.escape(bot_display)}",
                    "",
                    content,
                    flags=re.IGNORECASE,
                )

                content = re.sub(r'^[\s@:,\-]+', '', content)
                content = re.sub(r'\s{2,}', ' ', content)

            content = content.strip()

            messages.insert(
                0,
                {
                    "role": "user" if msg.author != self.bot.user else "assistant",
                    "name": author_name,
                    "content": content,
                },
            )

        return messages

    @commands.Cog.listener()
    async def on_message(self, message) -> None:

        if message.author == self.bot.user:
            return

        if self.bot.user in message.mentions:
            messages = await self.get_channel_history(message.channel.history(limit=10))

            self.local_memory = self.memory.search_memory(
                message.author.id, message.content
            )

            # search_res = await self.tools.web_search(message.content)

            system_prompt = f"""\
                You are a Discord-based assistant with memory and a dry sense of humor.
                Do NOT include any tags like <|start|>, <|end|>, <|assistant|>, <|channel|>, <|message|>, or tool-call wrappers.
                Use Discord markdown for emphasis, respond helpfully.

                [Memory]
                {self.local_memory if self.local_memory else "None"}
                """

            async with message.channel.typing():
                is_first_chunk = True
                inside_think = False
                buffer_rate = 175
                reply = ""
                buffer = ""
                sent = None

                async for token in self.lm_client.stream(messages, system_prompt):
                    buffer += token

                    if "<think>" in buffer:
                        buffer = ""  # discard start tag
                        inside_think = True
                        continue

                    if "</think>" in buffer:
                        buffer = ""  # discard end tag
                        inside_think = False
                        continue

                    if inside_think:
                        continue

                    reply += token

                    if is_first_chunk and reply.strip():
                        sent = await message.reply(content=reply.rstrip())
                        is_first_chunk = False

                    if len(buffer) > buffer_rate:
                        if sent is not None:
                            await sent.edit(content=reply.rstrip())
                        buffer = ""
            if sent is not None:
                await sent.edit(content=reply.rstrip())
            else:
                await message.channel.send(
                    "Sorry, I couldn't generate a response ⛓️‍💥 (Is the API online?)."
                )

            asyncio.create_task(
                self.memory.update_memory(
                    message.author.id, message.content, reply.rstrip()
                )
            )


async def setup(bot):
    await bot.add_cog(Events(bot))
