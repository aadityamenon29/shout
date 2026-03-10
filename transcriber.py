import os
import threading

from pywhispercpp.model import Model

MODEL_DIR = os.path.expanduser("~/.local/share/shout/models")
MODEL_NAME = "ggml-small.en.bin"

_model: Model | None = None
_lock = threading.Lock()


def get_model() -> Model:
    global _model
    with _lock:
        if _model is None:
            model_path = os.path.join(MODEL_DIR, MODEL_NAME)
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f"Whisper model not found at {model_path}\n"
                    "Run: make setup"
                )
            print(f"[shout] Loading model: {MODEL_NAME}")
            _model = Model(model_path, print_realtime=False, print_progress=False)
            print("[shout] Model loaded")
        return _model


def transcribe(wav_path: str) -> str:
    model = get_model()
    segments = model.transcribe(wav_path)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text
