from PyQt6.QtCore import QThread
from ui.widget_conf.ui_utils import SetStyleSheetForbtn
from ui.main_ui import Ui_MainWindow
from thread_speak import SpeakThread
from thread_listen import ListenThread
from thread_response import ResponseThread
from thread_welcome import WelcomeThread

class QnaPage:
    def __init__(self, main: Ui_MainWindow, initial_context):
        self.ui = main
        self.initial_context = initial_context

        self.ui.btn_micro.clicked.connect(lambda: [self.listen(), self.ui.btn_home_qna.setEnabled(False), SetStyleSheetForbtn(self.ui, "btn_micro", "#69ff3d")])
        self.ui.btn_home_qna.clicked.connect(lambda: [self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)])

    def start_welcome(self):
        SetStyleSheetForbtn(self.ui, "btn_speaker", "#69ff3d")
        self.welcome_thread = WelcomeThread()
        self.welcome_thread.finished.connect(lambda: [self.cleanup_thread(self.welcome_thread), self.ui.btn_home_qna.setEnabled(True), self.ui.btn_micro.setEnabled(True),
                                                    SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff")])
        self.welcome_thread.start()

    def listen(self):
        self.ui.btn_home_qna.setEnabled(False)
        self.ui.prompt_qna.setText("Listening...")
        self.listen_thread = ListenThread()
        self.listen_thread.finished.connect(self.get_response)
        self.listen_thread.finished.connect(lambda: [self.cleanup_thread(self.listen_thread), self.ui.btn_micro.setEnabled(False), 
                                                    SetStyleSheetForbtn(self.ui, "btn_micro", "#ffffff"), SetStyleSheetForbtn(self.ui, "btn_speaker", "#69ff3d")])
        self.listen_thread.start()

    def get_response(self, query: str):
        self.query = query
        if self.query == "Are you still there?" or self.query == "Hmm, I didn't quite catch that. Could you please repeat?" or self.query == "Something went wrong while listening." or self.query == "Speech service is unavailable.":
            print(f"AIko: {query}")
            self.ui.prompt_qna.setText(self.query)
            self.speak_thread = SpeakThread(self.query)
            self.speak_thread.finished.connect(lambda: [self.cleanup_thread(self.speak_thread), self.ui.btn_micro.setEnabled(True), self.ui.btn_home_qna.setEnabled(True),
                                                        SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff")])
            self.speak_thread.start()
        else:
            self.query = query.lower()
            print(f"You: {self.query}")
            self.response_thread = ResponseThread(self.query, intial_context=self.initial_context)
            self.response_thread.finished.connect(self.answer)
            self.response_thread.finished.connect(lambda: [self.cleanup_thread(self.response_thread)])
            self.response_thread.start()

    def answer(self, text: str):
        self.ui.prompt_qna.setText(text)
        self.speak_thread = SpeakThread(text)
        self.speak_thread.finished.connect(lambda: [self.cleanup_thread(self.speak_thread), SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff"), 
                                                    self.ui.btn_home_qna.setEnabled(True), self.ui.btn_micro.setEnabled(True)])
        self.speak_thread.start()

    def cleanup_thread(self, thread: QThread):
        if thread:
            thread.quit()
            thread.wait()
            thread.deleteLater()
