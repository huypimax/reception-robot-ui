from PyQt6.QtCore import QThread
import asyncio
from edge_tts import Communicate
import playsound
import os
import uuid
import tempfile
import time


class SpeakThread(QThread):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.speak(self.text))
        loop.close()

    async def speak(self, text):
        try:
            # Create a unique temporary mp3 file
            tmp_file = os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex}.mp3")

            # Generate speech
            communicate = Communicate(text, voice="en-US-GuyNeural", rate="-10%")
            await communicate.save(tmp_file)

            # Play and wait for completion
            playsound.playsound(tmp_file, block=True)

            # Retry deletion in case of slight file lock delay
            for _ in range(10):
                try:
                    os.remove(tmp_file)
                    break
                except PermissionError:
                    time.sleep(0.1)

        except Exception as e:
            print("🔊 Error in thread speak:", e)
