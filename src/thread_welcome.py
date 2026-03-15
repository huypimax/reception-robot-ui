from PyQt6.QtCore import QThread
import datetime
from language_manager import get_language_manager, get_string
import utilities.string_ids as stringIds

class WelcomeThread(QThread):
    def __init__(self, speaker, parent=None):
        super().__init__(parent)
        self.speaker = speaker
        self.lang_manager = get_language_manager()

    def run(self):
        hour = datetime.datetime.now().hour

        if 6 <= hour < 12:
            greet = get_string(stringIds.WELCOME_GOOD_MORNING)
        elif 12 <= hour < 18:
            greet = get_string(stringIds.WELCOME_GOOD_AFTERNOON)
        else:
            greet = get_string(stringIds.WELCOME_GOOD_EVENING)

        greeting_text = get_string(stringIds.WELCOME_GREETING)
        text = f"{greet}, {greeting_text}"
        self.speaker.say(text)
