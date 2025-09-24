import discord
from discord.ext import commands
from discord.ext.voice_recv import BasicSink, VoiceData, VoiceRecvClient
import wave
import tempfile
import asyncio
from collections import defaultdict
import time, os

from utils.stt import stream_transcribe
from utils.tts import speak_reply

discord.opus._load_default()

# 👇 trigger words you want users to start with
TRIGGER_WORDS = os.getenv("VOICE_TRIGGER_WORDS", "hey bot,ok bot,hello bot").lower().split(",")

class UserSink(BasicSink):
    def __init__(self, responder, channel, vc):
        super().__init__(self.on_packet)
        self.responder = responder
        self.channel = channel
        self.vc = vc
        self.buffers = defaultdict(list)
        self.last_spoke = {}
        self.speaking_threshold = 2

        #self.isTalking = False

        asyncio.create_task(self.monitor_speaking())

    def on_packet(self, user, data: VoiceData):
        self.buffers[user.id].append(data.pcm)
        self.last_spoke[user.id] = time.time()

    async def monitor_speaking(self):
        while self.vc.is_connected():
            now = time.time()
            for user_id in list(self.buffers.keys()):
                last_time = self.last_spoke.get(user_id, 0)
                if now - last_time > self.speaking_threshold:
                    await self.stop_and_process(user_id)
            await asyncio.sleep(1)

    async def stop_and_process(self, user_id):
        pcm_data = b"".join(self.buffers.pop(user_id, []))
        self.last_spoke.pop(user_id, None)

        if not pcm_data:
            return
        
        if len(pcm_data) < 48000 * 1:  # ignore <1s
            return

        user = self.vc.guild.get_member(user_id)
        if not user:
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            with wave.open(temp_wav.name, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(94000)
                wf.writeframes(pcm_data)

            transcript = ""
            for chunk in stream_transcribe(temp_wav.name):
                transcript += chunk

        if not transcript.strip():
            return

        lowered = transcript.lower().strip()
        if not any(lowered.startswith(word) for word in TRIGGER_WORDS):
            print(f"Ignoring (no trigger word): {transcript}")
            return

        await self.channel.send(f"**{user.display_name} said:** {transcript}")

        reply_text = ""
        system_prompt = """
            You are a Discord-based voice assistant with a sense of humor.
            Respond ONLY with text to be spoken aloud. Do not include any symbols, markdown or emojis.
            Keep responses brief and to the point.
        """
        async for chunk in self.responder.lm_client.stream([{"role":"user", "name": user.display_name, "content": transcript}], system_prompt):
            reply_text += chunk

        await self.channel.send(f"**AI replied:** {reply_text}")
        tts_path = f"/tmp/reply_{user.id}.wav"
        reply_text = reply_text.removeprefix("text:").strip()
        speak_reply(reply_text, tts_path)
        if not self.vc.is_playing() and self.vc.is_connected():
            self.vc.play(discord.FFmpegPCMAudio(tts_path))



class VoiceResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lm_client = bot.lm_client
        self.voice_clients = {}
        self.user_sinks = {}

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice:
            vc = await ctx.author.voice.channel.connect(cls=VoiceRecvClient)
            vc.play(discord.FFmpegPCMAudio("../audio/silence.mp3"))
            self.voice_clients[ctx.guild.id] = vc

            channel = ctx.channel
            sink = UserSink(self, channel, vc)
            self.user_sinks[ctx.guild.id] = sink
            vc.listen(sink)

            await ctx.send("Joined voice channel and listening.")
        else:
            await ctx.send("You're not in a voice channel.")

    @commands.command()
    async def leave(self, ctx):
        vc = self.voice_clients.get(ctx.guild.id)
        if vc:
            vc.stop_listening()
            await vc.disconnect()
            del self.voice_clients[ctx.guild.id]
            self.user_sinks.pop(ctx.guild.id, None)
            await ctx.send("Left the VC and stopped listening.")


async def setup(bot):
    await bot.add_cog(VoiceResponder(bot))
