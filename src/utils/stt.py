import os
import whisper

model = whisper.load_model("turbo")

def transcribe_audio(path):
    result = model.transcribe(
        path,
        language="en",
        fp16=False,
        verbose=False
    )
    return result["text"]
