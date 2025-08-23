from faster_whisper import WhisperModel

# pick a model: "tiny", "base", "small", "medium", "large-v2"
# "small" is a good balance for speed/accuracy
model = WhisperModel("small", device="cpu", compute_type="int8")

def stream_transcribe(path: str):
    segments, _ = model.transcribe(path, beam_size=1, vad_filter=True, language="en")
    for s in segments:
        yield s.text
