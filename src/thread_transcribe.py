# thread_transcribe.py
from PyQt6.QtCore import QThread, pyqtSignal
from silero_vad import load_silero_vad, get_speech_timestamps
from queue import Queue
import numpy as np
import whisper


class TranscribeThread(QThread):
    text_ready = pyqtSignal(tuple)  # (text, lang)

    def __init__(self, audio_queue: Queue, device="cpu"):
        super().__init__()
        self.audio_queue = audio_queue
        self.running = True
        self.device = device
        self.model = None
        self.vad = load_silero_vad()

    def run(self):
        if self.model is None:
            self.model = whisper.load_model("tiny", device=self.device)

        while self.running:
            try:
                audio_np = self.audio_queue.get(timeout=1)

                if audio_np is None or audio_np.size == 0:
                    continue

                timestamps = get_speech_timestamps(
                    audio_np,
                    self.vad,
                    sampling_rate=16000,
                    threshold=0.35,
                    min_speech_duration_ms=50,
                    max_speech_duration_s=15,
                    min_silence_duration_ms=100,
                    speech_pad_ms=30,
                )

                if not timestamps:
                    continue

                # Ghép toàn bộ đoạn có tiếng
                speech_audio = np.concatenate(
                    [audio_np[t["start"]:t["end"]] for t in timestamps]
                )

                if speech_audio.size < 1000:
                    continue

                # Whisper
                result = self.model.transcribe(speech_audio, language=None, fp16=False)
                text = result["text"].strip()

                if not text or len(text) <= 2:
                    continue

                lang = result.get("language", "en")
                lang = lang if lang in ["vi", "en"] else "en"

                print(f"Người nói: {text} ({lang})")
                self.text_ready.emit((text, lang))

            except Exception as e:
                print("Transcribe error:", e)

    def stop(self):
        self.running = False
        self.quit()
        self.wait(3000)
