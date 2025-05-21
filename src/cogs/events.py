import discord, asyncio
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lm_client = bot.lm_client
        self.memory = bot.memory
        self.tools = bot.tools
        self.local_memory = None
        self.i = 5

    async def get_channel_history(self, history) -> str:
        history = [msg async for msg in history]
        messages = []

        for msg in history:
            messages.insert(
                0,
                f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {msg.author.name}: {msg.content}",
            )
        recent = "\n".join(messages)

        return recent

    @commands.Cog.listener()
    async def on_message(self, message) -> None:

        if message.author == self.bot.user:
            return

        if (
            self.bot.user.name.lower() in message.content.lower()
            or self.bot.user in message.mentions
        ):
            recent = await self.get_channel_history(message.channel.history(limit=10))

            self.i += 1
            if self.i > 5:
                asyncio.create_task(
                    self.memory.update_memory(message.author.id, self.bot.user.name, recent)
                )
                self.local_memory = self.memory.get_memory(message.author.id)
                self.i = 0

            #search_res = await self.tools.web_search(message.content)

            system_prompt = f"""\
                You are {self.bot.user.name}, a Discord-based assistant with memory and a dry sense of humor.
                Respond informally and helpfully, using provided memory to act like you've been part of the conversation.
                Avoid exaggeration or cheesy replies and use modern humor.
                Write your response in clean paragraphs with no more than **one** blank line between sections. Do not add extra line breaks or spacing.
                Use Discord markdown for emphasis.

                [Memory]
                {self.local_memory}

                [Recent Messages]
                {recent}
                """
            prompt = f"{message.author.name}: {message.content}\nBob:"

            async with message.channel.typing():
                is_first_chunk = True
                inside_think = False
                buffer_rate = 175
                reply = ""
                buffer = ""
                sent = None

                async for token in self.lm_client.stream(prompt, system_prompt):
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
            elif reply.strip():
                await message.channel.send(content=reply.rstrip())
            else:
                await message.channel.send(
                    "Sorry, I couldn't generate a response ⛓️‍💥 (Is the API online?)."
                )


async def setup(bot):
    await bot.add_cog(Events(bot))
