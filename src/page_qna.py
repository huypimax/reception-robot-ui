from PyQt6.QtCore import QThread
from ui.widget_conf.ui_utils import SetStyleSheetForbtn
from ui.main_ui import Ui_MainWindow

from thread_speak import SpeakThread
from thread_listen import ListenThread
from thread_transcribe import TranscribeThread
from thread_response import ResponseThread, get_weather, search_web
from thread_welcome import WelcomeThread

from google.genai import Client, types

import os
import json
from queue import Queue


ASSISTANT_NAME = "AIko"

conversation_history = [
    {
        "role": "user",
        "parts": [{"text": "You are AIko, a friendly, concise receptionist assistant from Fablab HCMUT."}]
    },
    {
        "role": "model",
        "parts": [{"text": "Got it! I'm AIko, nice to meet you."}]
    },
]

MODEL_NAME = "gemini-2.5-pro"
ALL_TOOLS = [get_weather, search_web]


class QnaPage:
    def __init__(self, main: Ui_MainWindow, initial_context):
        self.ui = main
        self.initial_context = initial_context

        self.ui.btn_micro.clicked.connect(
            lambda: [
                self.listen(),
                self.ui.btn_home_qna.setEnabled(False),
                SetStyleSheetForbtn(self.ui, "btn_micro", "#69ff3d")
            ]
        )

        self.ui.btn_home_qna.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)
        )

        # Load API key
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "config.json")

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        self.api_key = config["gemini_api_key"]
        self.client = Client(api_key=self.api_key)

        # Global chat session
        generation_config = types.GenerateContentConfig(tools=ALL_TOOLS)
        self.global_chat_session = self.client.chats.create(
            model=MODEL_NAME,
            history=conversation_history,
            config=generation_config
        )

        # Audio pipeline
        self.audio_queue = Queue()
        self.listen_thread = ListenThread(self.audio_queue)
        self.transcribe_thread = TranscribeThread(self.audio_queue, device="cpu")
        self.transcribe_thread.text_ready.connect(self.handle_text)

    def start_welcome(self):
        SetStyleSheetForbtn(self.ui, "btn_speaker", "#69ff3d")

        self.welcome_thread = WelcomeThread()
        self.welcome_thread.finished.connect(
            lambda: [
                self.cleanup_thread(self.welcome_thread),
                self.ui.btn_home_qna.setEnabled(True),
                self.ui.btn_micro.setEnabled(True),
                SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff")
            ]
        )

        self.welcome_thread.start()

    def listen(self):
        self.ui.btn_home_qna.setEnabled(False)
        self.ui.prompt_qna.setText("Listening...")

        self.ui.btn_micro.setEnabled(False)
        SetStyleSheetForbtn(self.ui, "btn_micro", "#ffffff")
        SetStyleSheetForbtn(self.ui, "btn_speaker", "#69ff3d")

        # Xóa queue để tránh sót âm thanh cũ
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                break

        self.listen_thread.start()
        self.transcribe_thread.start()

    def handle_text(self, result):
        text, lang = result
        text = text.strip()

        if not text or len(text) <= 2:
            return

        if text.lower() in ["thanks", "thank you", "you", "...", "hmm"]:
            return

        self.get_response(text, lang)

    def get_response(self, query, lang):
        print(f"You ({lang}): {query}")

        if query in [
            "Are you still there?",
            "Hmm, I didn't quite catch that. Could you please repeat?",
            "Something went wrong while listening.",
            "Speech service is unavailable."
        ]:
            self.ui.prompt_qna.setText(self.query)
            self.speak_thread = SpeakThread(self.query)

            self.speak_thread.finished.connect(
                lambda: [
                    self.cleanup_thread(self.speak_thread),
                    self.ui.btn_micro.setEnabled(True),
                    self.ui.btn_home_qna.setEnabled(True),
                    SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff"),
                ]
            )

            self.speak_thread.start()
            return

        self.query = query.lower()

        self.response_thread = ResponseThread(
            self.query,
            chat_session=self.global_chat_session,
            initial_context=self.initial_context,
            lang=lang
        )

        self.response_thread.finished.connect(self.answer)
        self.response_thread.finished.connect(
            lambda: self.cleanup_thread(self.response_thread)
        )
        self.response_thread.start()

    def stop_listening(self):
        if self.listen_thread.isRunning():
            self.listen_thread.stop()
            self.listen_thread.wait()

        if self.transcribe_thread.isRunning():
            self.transcribe_thread.stop()
            self.transcribe_thread.wait()

        self.ui.btn_micro.setEnabled(True)
        self.ui.btn_home_qna.setEnabled(True)
        SetStyleSheetForbtn(self.ui, "btn_micro", "#69ff3d")

    def answer(self, text: str):
        self.ui.prompt_qna.setText(text)

        self.speak_thread = SpeakThread(text)
        self.speak_thread.finished.connect(
            lambda: [
                self.cleanup_thread(self.speak_thread),
                SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff"),
                self.ui.btn_home_qna.setEnabled(True),
                self.ui.btn_micro.setEnabled(True),
                self.stop_listening(),
            ]
        )

        self.speak_thread.start()

    def cleanup_thread(self, thread: QThread):
        if thread:
            thread.quit()
            thread.wait()
            thread.deleteLater()
