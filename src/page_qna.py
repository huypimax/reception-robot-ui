from PyQt6.QtCore import QTimer
from ui.widget_conf.ui_utils import SetStyleSheetForbtn
from ui.main_ui import Ui_MainWindow
from speak_thread import SpeakThread
from listen_thread import ListenThread
from response_thread import ResponseThread
from welcome_thread import WelcomeThread

class QnaPage:
    def __init__(self, main: Ui_MainWindow, initial_context):
        self.ui = main
        self.initial_context = initial_context
        self.micro_loop = False
        self.silent_count = 0
        self.setup_connections()

    def setup_connections(self):
        self.ui.btn_micro.clicked.connect(lambda: [self.handle_micro(), self.ui.btn_home_qna.setEnabled(False)])
        self.ui.btn_home_qna.clicked.connect(lambda: self.go_home())
        # Gọi hàm chào hỏi
        self.ui.btn_qna.clicked.connect(lambda: self.start_welcome())

    def start_welcome(self):
        SetStyleSheetForbtn(self.ui, "btn_speaker", "#69ff3d")
        self.welcome_thread = WelcomeThread()
        self.welcome_thread.finished.connect(lambda: [
            self.cleanup_thread(self.welcome_thread),
            self.ui.btn_home_qna.setEnabled(True),
            self.ui.btn_micro.setEnabled(True),
            SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff")
        ])
        self.welcome_thread.start()

    def handle_micro(self):
        if not self.micro_loop:
            self.micro_loop = True
            self.silent_count = 0
            self.listen()

    def listen(self):
        SetStyleSheetForbtn(self.ui, "btn_micro", "#69ff3d")
        self.ui.prompt_qna.setText("Listening...")
        self.listen_thread = ListenThread()
        self.listen_thread.finished.connect(self.get_response)
        self.listen_thread.finished.connect(lambda: [
            self.cleanup_thread(self.listen_thread),
            SetStyleSheetForbtn(self.ui, "btn_micro", "#ffffff")
        ])
        self.listen_thread.start()

    def get_response(self, query: str):
        self.query = query.lower()
        if not self.query:
            self.continue_conversation()
        else:
            self.response_thread = ResponseThread(self.query, intial_context=self.initial_context)
            self.response_thread.finished.connect(self.answer)
            self.response_thread.finished.connect(lambda: self.cleanup_thread(self.response_thread))
            self.response_thread.start()

    def answer(self, text: str):
        self.ui.prompt_qna.setText(text)
        self.speak_thread = SpeakThread(text)
        self.speak_thread.finished.connect(self.continue_conversation)
        self.speak_thread.finished.connect(lambda: self.cleanup_thread(self.speak_thread))
        self.speak_thread.start()

    def continue_conversation(self):
        self.listen()

    def go_home(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)

    def cleanup_thread(self, thread):
        if thread:
            thread.quit()
            thread.wait()
            thread.deleteLater()
