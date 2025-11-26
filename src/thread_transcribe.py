# thread_transcribe.py
from PyQt6.QtCore import QThread, pyqtSignal
from faster_whisper import WhisperModel
from silero_vad import load_silero_vad, get_speech_timestamps
from queue import Queue
import numpy as np

class TranscribeThread(QThread):
    """
    Thread lấy audio từ queue, VAD + Whisper small, emit (text, lang)
    """
    text_ready = pyqtSignal(tuple)  # (text, lang)

    def __init__(self, audio_queue: Queue, device="cpu"):
        super().__init__()
        self.audio_queue = audio_queue
        self.running = True

        # Load Silero VAD
        self.vad = load_silero_vad()
        # Load Whisper small
        self.model = WhisperModel("tiny", device=device, compute_type="int8")

    def run(self):
        while self.running:
            try:
                audio = self.audio_queue.get()
                if audio.size == 0:
                    continue

                # VAD: chỉ lấy phần có speech
                timestamps = get_speech_timestamps(audio, self.vad, sampling_rate=16000)
                if len(timestamps) == 0:
                    continue

                # Whisper transcription
                segments, info = self.model.transcribe(audio, beam_size=1)
                for seg in segments:
                    # detect ngôn ngữ Whisper trả về
                    lang = info.language if hasattr(info, "language") else "en"
                    if lang not in ["en", "vi"]:
                        lang = "en"  # mặc định sang English nếu Whisper detect khác
                    self.text_ready.emit((seg.text, lang))

            except Exception as e:
                print("📝 TranscribeThread error:", e)

    def stop(self):
        self.running = False
