from PyQt6.QtCore import QThread, pyqtSignal
from queue import Queue, Empty
import asyncio
from edge_tts import Communicate
import playsound
import os, uuid, tempfile, time


class SpeakThreadNew(QThread):
    finished_one = pyqtSignal(str)  # phát tín hiệu khi nói xong 1 câu

    def __init__(self):
        super().__init__()
        self.queue = Queue()
        self.running = True

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while self.running:
            try:
                text = self.queue.get(timeout=0.1)
            except Empty:
                continue

            loop.run_until_complete(self._speak(text))
            self.finished_one.emit(text)

        loop.close()

    async def _speak(self, text):
        try:
            tmp_file = os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex}.mp3")

            communicate = Communicate(text, voice="en-US-GuyNeural", rate="-10%")
            await communicate.save(tmp_file)

            playsound.playsound(tmp_file, block=True)

            for _ in range(10):
                try:
                    os.remove(tmp_file)
                    break
                except PermissionError:
                    time.sleep(0.1)

        except Exception as e:
            print("TTS error:", e)

    def say(self, text):
        self.queue.put(text)

    def stop(self):
        self.running = False


class SpeakManager:
    def __init__(self):
        self.thread = SpeakThreadNew()
        self.thread.start()

    def say(self, text):
        self.thread.say(text)

    def connect_finished(self, callback):
        self.thread.finished_one.connect(callback)
