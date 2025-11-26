from PyQt6.QtCore import QThread, pyqtSignal
import asyncio
import speech_recognition as sr

class ListenThread(QThread):
    finished = pyqtSignal(str)
    def __init__(self):
        super().__init__()

    def run(self):
        self.r = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Calibrating noise (1.0s)...")
            self.r.adjust_for_ambient_noise(source, duration=0.5)
            print("🎤 Listening...")
            try:
                self.audio = self.r.listen(source, timeout=6, phrase_time_limit=12)
                self.query = self.r.recognize_google(self.audio, language="en-US")
                print("You:", self.query)
                self.finished.emit(self.query)
                return
            except sr.UnknownValueError:
                self.finished.emit("Hmm, I didn't quite catch that. Could you please repeat?")
                return
            except sr.RequestError:
                self.finished.emit("Speech service is unavailable.")
                return
            except sr.WaitTimeoutError:
                self.finished.emit("Are you still there?")
                return
            except Exception as e:
                print("🎤 Error:", e)
                self.finished.emit("Something went wrong while listening.")
                return
        self.finished.emit("Speech service is unavailable.")
        return

# from PyQt6.QtCore import QThread, pyqtSignal
# import speech_recognition as sr

# class ListenThread(QThread):
#     finished = pyqtSignal(str)

#     def __init__(self, lang="auto"):
#         super().__init__()
#         self.lang = lang  # "auto", "en", "vi", "ja"

#     def detect_language(self, text):
#         # simple heuristic
#         if any(ch in text for ch in "あいうえおかきくけこ"):
#             return "ja-JP"
#         if any(ch in text for ch in "áàảãạăắằẳẵặâấầẩẫậđêếềểễệôốồổỗộơớờởỡợưứừửữự"):
#             return "vi-VN"
#         return "en-US"

#     def run(self):
#         r = sr.Recognizer()

#         try:
#             with sr.Microphone() as source:
#                 print("🎤 Calibrating noise (1.0s)...")
#                 r.adjust_for_ambient_noise(source, duration=1.0)

#                 print("🎤 Listening...")
#                 audio = r.listen(source, timeout=6, phrase_time_limit=10)

#                 # Auto language
#                 if self.lang == "auto":
#                     lang = "en-US"  # default safe
#                 elif self.lang == "vi":
#                     lang = "vi-VN"
#                 elif self.lang == "ja":
#                     lang = "ja-JP"
#                 else:
#                     lang = "en-US"

#                 text = r.recognize_google(audio, language=lang)

#                 # auto adjust language (optional)
#                 if self.lang == "auto":
#                     lang = self.detect_language(text)

#                 print(f"User ({lang}):", text)
#                 self.finished.emit(text)
#                 return

#         except sr.WaitTimeoutError:
#             self.finished.emit("Are you still there?")
#         except sr.UnknownValueError:
#             self.finished.emit("I didn't catch that. Could you repeat?")
#         except sr.RequestError:
#             self.finished.emit("Speech service is unavailable.")
#         except Exception as e:
#             print("🎤 Error:", e)
#             self.finished.emit("Something went wrong while listening.")

