# thread_listen.py
from PyQt6.QtCore import QThread
import sounddevice as sd
import numpy as np
from queue import Queue

class ListenThread(QThread):
    """
    Thread liên tục đọc micro và push audio vào queue
    """
    def __init__(self, audio_queue: Queue, samplerate=16000, chunk=2048):
        super().__init__()
        self.audio_queue = audio_queue
        self.running = True
        self.samplerate = samplerate
        self.chunk = chunk

    def run(self):
        while self.running:
            try:
                audio = sd.rec(self.chunk, samplerate=self.samplerate, channels=1, dtype='float32')
                sd.wait()
                # Push audio dạng 1D float32
                self.audio_queue.put(audio.flatten())
            except Exception as e:
                print("🎤 ListenThread error:", e)
                # Nếu có lỗi, push empty array để TranscribeThread nhận và skip
                self.audio_queue.put(np.array([], dtype=np.float32))

    def stop(self):
        self.running = False
