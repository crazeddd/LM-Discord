import wave
from piper.voice import PiperVoice

def speak_reply(text: str, output_path: str = "out.wav"):
    model_path = "audio/tts_models/en_US-amy-medium.onnx"
    config_path = "audio/tts_models/en_US-amy-medium.onnx.json"

    voice = PiperVoice.load(model_path, config_path)

    audio_chunks = list(voice.synthesize(text))
    if not audio_chunks:
        print("[TTS] No audio generated.")
        return

    audio_data = b''.join(chunk.audio_int16_bytes for chunk in audio_chunks)

    # Save to proper WAV file
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(audio_chunks[0].sample_channels)
        wf.setsampwidth(audio_chunks[0].sample_width)
        wf.setframerate(audio_chunks[0].sample_rate)
        wf.writeframes(audio_data)
