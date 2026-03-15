# ------------------------------------------------------------------------
# speak_thread.py
# Thread chỉ lo TTS, không init mixer, không quit mixer
# ------------------------------------------------------------------------
from PyQt6.QtCore import QThread, pyqtSignal
from queue import Queue, Empty
import asyncio, os, uuid, tempfile
from edge_tts import Communicate
import pygame
from mixer import play_audio, stop_audio
from language_manager import get_language_manager
import utilities.constants as constants

class SpeakThread(QThread):
    finished_one = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.queue = Queue()
        self.running = True
        self._stop_current = False
    
    def _get_tts_voice(self):
        lang_manager = get_language_manager()
        current_lang = lang_manager.get_current_language()
        voice = constants.TTS_VOICES.get(current_lang, "en-US-GuyNeural")
        print(f"TTS: Current language is '{current_lang}', selected voice is '{voice}'")
        return voice

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while self.running:
            try:
                text = self.queue.get(timeout=0.1)
                if text is None:
                    break
            except Empty:
                continue
            if not self.running:
                break
            loop.run_until_complete(self._speak(text))
            if self.running and not self._stop_current:
                self.finished_one.emit(text)
            self.queue.task_done()

        loop.close()

    async def _speak(self, text):
        self._stop_current = False
        temp_path = os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex}.mp3")

        try:
            # tạo file mp3
            voice = self._get_tts_voice()
            comm = Communicate(text, voice=voice, rate="-10%")
            await comm.save(temp_path)
            # phát qua mixer toàn app
            play_audio(temp_path)
            # đợi phát xong hoặc bị stop
            while pygame.mixer.music.get_busy() and self.running and not self._stop_current:
                await asyncio.sleep(0.05)

            stop_audio()

            for _ in range(10):
                try:
                    os.remove(temp_path)
                    break
                except:
                    await asyncio.sleep(0.1)

        except Exception as e:
            print("TTS error:", e)

    def say(self, text):
        if self.running:
            self.queue.put(text)

    def stop_current(self):
        self._stop_current = True
        stop_audio()
        # clear queue
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except:
                break

    def shutdown(self):
        self.running = False
        self.stop_current()
        self.queue.put(None)


# ------------------------------------------------------------------------
# speak_manager.py
# Quản lý thread nhưng KHÔNG quit mixer
# ------------------------------------------------------------------------

class SpeakManager:
    def __init__(self):
        self.thread = None
        self.start()

    def start(self):
        if self.thread is None or not self.thread.isRunning():
            self.thread = SpeakThread()
            self.thread.start()

    def say(self, text):
        if self.thread and self.thread.isRunning():
            self.thread.say(text)

    def stop(self):
        if self.thread:
            self.thread.stop_current()

    def connect_finished(self, callback):
        if self.thread:
            self.thread.finished_one.connect(callback)

    def shutdown(self):
        if self.thread:
            self.thread.shutdown()
            self.thread.wait(3000)
            self.thread = None