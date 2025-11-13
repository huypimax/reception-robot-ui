from PyQt6.QtCore import QThread
import asyncio
from edge_tts import Communicate
from pydub import AudioSegment
from pydub.playback import play
import os
import uuid
import tempfile
import time

class SpeakThread(QThread):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        # Tạo event loop riêng cho thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.speak(self.text))
        loop.close()

    async def speak(self, text):
        try:
            # Tạo file mp3 tạm thời duy nhất
            tmp_file = os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex}.mp3")

            # Tạo giọng nói
            communicate = Communicate(text, voice="en-US-GuyNeural", rate="-10%")
            await communicate.save(tmp_file)

            # Chạy phát âm thanh
            audio = AudioSegment.from_file(tmp_file)
            play(audio)

            # Xóa file tạm
            for _ in range(10):
                try:
                    os.remove(tmp_file)
                    break
                except PermissionError:
                    time.sleep(0.1)

        except Exception as e:
            print("🔊 Error in thread speak:", e)
