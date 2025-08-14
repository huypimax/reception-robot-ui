import asyncio
import datetime
import os
import uuid
import tempfile
import pygame
from PyQt6.QtCore import QThread
from edge_tts import Communicate

class WelcomeThread(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        hour = datetime.datetime.now().hour
        if 6 <= hour < 12:
            greet = "Good morning"
        elif 12 <= hour < 18:
            greet = "Good afternoon"
        else:
            greet = "Good evening"

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            self._speak(f"AIko {greet}, I'm AIko, your receptionist assistant, how can I help you?")
        )
        loop.close()

    async def _speak(self, text):
        try:
            # Use a temp file to avoid conflicts
            tmp_file = os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex}.mp3")

            communicate = Communicate(text, voice="en-US-GuyNeural")
            await communicate.save(tmp_file)

            # Initialize pygame mixer
            pygame.mixer.init()
            pygame.mixer.music.load(tmp_file)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)

            pygame.mixer.quit()
            os.remove(tmp_file)

        except Exception as e:
            print("🔊 Error in thread welcome:", e)
