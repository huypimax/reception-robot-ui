from PyQt6.QtCore import QThread
import datetime

class WelcomeThread(QThread):
    def __init__(self, speaker, parent=None):
        super().__init__(parent)
        self.speaker = speaker

    def run(self):
        hour = datetime.datetime.now().hour

        if 6 <= hour < 12:
            greet = "Good morning"
        elif 12 <= hour < 18:
            greet = "Good afternoon"
        else:
            greet = "Good evening"

        text = f"{greet}, I'm AIko, how can I help you?"
        self.speaker.say(text)
