from PyQt6.QtCore import QThread
from ui.widget_conf.ui_utils import SetStyleSheetForbtn, _animate_prompt
from ui.main_ui import Ui_MainWindow
from thread_speak import SpeakThread
from thread_listen import ListenThread
from thread_response import ResponseThread
from thread_welcome import WelcomeThread
import os, json
from queue import Queue
from thread_speak import SpeakManager
from ai.response_graph import ResponseGraph
from language_manager import get_language_manager, get_string
import utilities.string_ids as stringIds
import utilities.constants as constants

class QnaPage:
    def __init__(self, main: Ui_MainWindow, initial_context):
        self.ui = main
        self.initial_context = initial_context
        self.speaker = SpeakManager()
        self.lang_manager = get_language_manager()

        self.ui.btn_micro.clicked.connect(lambda: [self.listen(), self.ui.btn_home_qna.setEnabled(False)])
        self.ui.btn_home_qna.clicked.connect(lambda: [self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)])

        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        self.api_key = config["gemini_api_key"]
        
        self.response_graph = ResponseGraph(
            api_key=self.api_key,
            model_name=constants.MODEL_NAME,
            initial_context=self.initial_context
        )

    def start_welcome(self):
        SetStyleSheetForbtn(self.ui, "btn_speaker", "#69ff3d", hover_background="#69ff3d")
        self.welcome_thread = WelcomeThread(self.speaker)
        self.welcome_thread.finished.connect(lambda: [self.cleanup_thread(self.welcome_thread), self.ui.btn_home_qna.setEnabled(True), self.ui.btn_micro.setEnabled(True)])
        self.welcome_thread.start()

    def listen(self):
        self.ui.btn_home_qna.setEnabled(False)
        self.start_animate(get_string(stringIds.QNA_LISTENING), self.ui.prompt_qna)
        SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff", hover_background="#ffffff")
        SetStyleSheetForbtn(self.ui, "btn_micro", "#69ff3d", hover_background="#69ff3d")
        self.listen_thread = ListenThread()
        self.listen_thread.finished.connect(self.get_response)
        # self.listen_thread.finished.connect(lambda: [self.cleanup_thread(self.listen_thread), self.ui.btn_micro.setEnabled(False), 
        #                                             SetStyleSheetForbtn(self.ui, "btn_micro", "#ffffff", hover_background="#ffffff"), SetStyleSheetForbtn(self.ui, "btn_speaker", "#69ff3d", hover_background="#69ff3d")])
        self.listen_thread.start()

    def get_response(self, query: str):
        self.stop_animate()
        self.cleanup_thread(self.listen_thread)
        self.ui.btn_micro.setEnabled(False)

        self.query = query
        error_messages = [
            get_string(stringIds.ERROR_STILL_THERE),
            get_string(stringIds.ERROR_LISTENING),
            get_string(stringIds.ERROR_SOMETHING_WRONG),
            get_string(stringIds.ERROR_SPEECH_UNAVAILABLE)
        ]
        if self.query in error_messages:
            print(f"AIko: {query}")
            self.ui.prompt_qna.setText(self.query)
            SetStyleSheetForbtn(self.ui, "btn_micro", "#ffffff", hover_background="#ffffff")
            SetStyleSheetForbtn(self.ui, "btn_speaker", "#69ff3d", hover_background="#69ff3d")
            self.speaker.say(self.query)
            self.speaker.connect_finished(lambda: [self.ui.btn_micro.setEnabled(True), self.ui.btn_home_qna.setEnabled(True),
                                                        SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff", hover_background="#ffffff")])
            # self.speak_thread.start()
        else:
            self.query = query.lower()
            print(f"You: {self.query}")
            # Sử dụng ResponseGraph thay vì chat_session
            self.response_thread = ResponseThread(
                query=self.query, 
                response_graph=self.response_graph
            )
            self.start_animate(get_string(stringIds.QNA_FINDING_ANSWER), self.ui.prompt_qna)
            SetStyleSheetForbtn(self.ui, "btn_micro", "#ffffff", hover_background="#ffffff")
            SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff", hover_background="#ffffff")

            self.response_thread.finished.connect(self.answer)
            self.response_thread.finished.connect(lambda: [self.cleanup_thread(self.response_thread)])
            self.response_thread.start()

    def answer(self, text: str):
        self.stop_animate()
        self.ui.prompt_qna.setText(text)
        SetStyleSheetForbtn(self.ui, "btn_micro", "#ffffff", hover_background="#ffffff")
        SetStyleSheetForbtn(self.ui, "btn_speaker", "#69ff3d", hover_background="#69ff3d")
        self.speaker.say(text)
        self.speaker.connect_finished(lambda: [SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff", hover_background="#ffffff"), 
                                                    self.ui.btn_home_qna.setEnabled(True), self.ui.btn_micro.setEnabled(True)])
        # self.speak_thread.start()


    def cleanup_thread(self, thread: QThread):
        if thread:
            thread.quit()
            thread.wait()
            thread.deleteLater()

    def start_animate(self, text, widget):
        if hasattr(self, "stop_prompt") and self.stop_prompt:
            self.stop_prompt()
        self.stop_prompt = _animate_prompt(base_text=text, label_widget=widget)

    def stop_animate(self):
        if hasattr(self, "stop_prompt") and self.stop_prompt:
            self.stop_prompt()
            self.stop_prompt = None
    
    def set_language_manager(self, lang_manager):
        self.lang_manager = lang_manager
    
    def update_language(self):
        if hasattr(self, 'response_graph'):
            self.response_graph.reset_conversation()
        
        self.ui.prompt_qna.setText(get_string(stringIds.QNA_TAP_MICROPHONE))