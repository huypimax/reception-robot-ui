# thread_listen.py
from PyQt6.QtCore import QThread
import sounddevice as sd
import numpy as np
from queue import Queue


class ListenThread(QThread):
    def __init__(self, audio_queue: Queue, samplerate=16000, chunk=2048, device=1):
        super().__init__()
        self.audio_queue = audio_queue
        self.running = True
        self.samplerate = samplerate
        self.chunk = chunk
        self.device = device  # Cho phép cấu hình, không hardcode vào run()

    def run(self):
        try:
            with sd.InputStream(
                samplerate=self.samplerate,
                channels=1,
                dtype="float32",
                blocksize=self.chunk,
                device=self.device
            ) as stream:
                print("Micro bật rồi, nói thử xem.")

                while self.running:
                    audio, overflowed = stream.read(self.chunk)

                    if overflowed:
                        print("Micro bị overflow")
                        continue

                    volume = np.linalg.norm(audio)
                    if volume > 10:
                        print(f"Phát hiện âm lượng: {volume:.1f}")

                    self.audio_queue.put(audio.flatten())

        except Exception as e:
            print("Lỗi ListenThread:", e)

    def stop(self):
        self.running = False
        self.quit()
        self.wait(3000)
