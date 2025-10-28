# --- main.py (đặt TRƯỚC mọi import PyQt) ---
import os
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join([
    "--enable-webgl",
    "--ignore-gpu-blocklist",
    "--enable-gpu-rasterization",
    "--enable-zero-copy",
    "--enable-accelerated-2d-canvas",
    "--use-angle=d3d11",                 # Windows IPC thường ổn nhất
    "--enable-features=CanvasOopRasterization",
    "--disable-software-rasterizer"
])
# Nếu máy có GPU rời: ép OpenGL desktop
# os.environ["QT_OPENGL"] = "desktop"


import sys
from ui.main_ui import Ui_MainWindow
from ui.fonts_conf.font_configurator import apply_custom_fonts
from ui.widget_conf.ui_utils import SetStyleSheetForbtn, _animate_prompt 
from ui.widget_conf.apply_utils import apply_shadow
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer

from mqtt_client import MQTTHandler
import asyncio
import os
from welcome_thread import WelcomeThread
from speak_thread import SpeakThread
from listen_thread import ListenThread
from response_thread import ResponseThread
from call_chatbot import AIkoBot
#from ui.web import WebTab
#from ui.web1 import WebTab1


ASSISTANT_NAME = "AIko"
initial_context = [
    {
        "role": "user",
        "parts": [
            {"text": "You are AIko, a helpful and concise virtual assistant created by Fablab."}
        ]
    },
    {
        "role": "model",
        "parts": [
            {"text": "Got it. I'm AIko, your assistant from Fablab."}
        ]
    },
    {
        "role": "user",
        "parts": [
            {"text": "When replying, use 1–2 full sentences, clear and friendly tone. Total word count must not exceed 35 words."}
        ]
    },
    {
        "role": "model",
        "parts": [
            {"text": "Understood. I’ll keep my answers short, friendly, and within 35 words."}
        ]
    }
]


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        apply_custom_fonts(self.ui)
        apply_shadow(self.ui)

        self.current_room = ""
        self.micro_loop = False
        self.silent_count = 0

        self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)

        # self.web_ = WebTab1(self.ui)
        # self.mqtt_handler = MQTTHandler(self.on_robot_status_update)
        # self.bot = AIkoBot()

        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(40000)  
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.go_to_main_page)

        # --- Logic điều hướng ---

        self.ui.btn_qna.clicked.connect(lambda: [self.handle_btn_qna(), self.ui.stackedWidget.setCurrentWidget(self.ui.page_qna), self.ui.prompt_qna.setText("Press the microphone button to start a conversation."), self.reset_inactivity_timer(), self.ui.btn_home_qna.setEnabled(False), self.ui.btn_micro.setEnabled(False)])
        self.ui.btn_navi.clicked.connect(lambda: [self.handle_btn_navi(), self.ui.stackedWidget.setCurrentWidget(self.ui.page_navi), self.reset_inactivity_timer(), self.ui.btn_home_navi.setEnabled(False), self._set_navigation_buttons_enabled(False), self.set_color_btn_room("#ffffff"), self.ui.prompt_navi.setText("Where do you want to go?")])
        self.ui.btn_lab.clicked.connect(lambda: [self.ui.stackedWidget.setCurrentWidget(self.ui.page_lab),self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_main)])
        self.ui.btn_deli.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_deli))
        self.ui.btn_check_in.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_checkin))

        self.ui.btn_home_qna.clicked.connect(lambda: self.go_to_main_page())
        self.ui.btn_home_navi.clicked.connect(lambda: self.go_to_main_page())
        self.ui.btn_home_deli.clicked.connect(lambda: self.go_to_main_page())
        self.ui.btn_home_checkin.clicked.connect(lambda: self.go_to_main_page())

        self.ui.btn_home_lab_main.clicked.connect(lambda: self.go_to_main_page())
        self.ui.btn_home_lab_IFM.clicked.connect(lambda: self.go_to_main_page())
        self.ui.btn_home_lab_PLC.clicked.connect(lambda: self.go_to_main_page())
        self.ui.btn_home_lab_step.clicked.connect(lambda: self.go_to_main_page())
        self.ui.btn_home_lab_HMI.clicked.connect(lambda: self.go_to_main_page())

        self.ui.btn_IFM_2.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_IFM))
        self.ui.btn_step_2.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_step))
        self.ui.btn_PLC.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_PLC))
        self.ui.btn_HMI.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_HMI))
        
        self.ui.btn_back_lab_IFM.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_main))
        self.ui.btn_back_lab_PLC.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_IFM))
        self.ui.btn_back_lab_step.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_main))
        self.ui.btn_back_lab_HMI.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_step))

        self.ui.btn_micro.clicked.connect(lambda: [self.handle_micro(), self.ui.btn_home_qna.setEnabled(False)])
        #self.ui.btn_speaker.setEnabled(False)

        # self.ui.btn_room_a.clicked.connect(lambda: [self.handle_go_to("A"), SetStyleSheetForbtn(self.ui, "btn_room_a", "#69ff3d")])
        # self.ui.btn_room_b.clicked.connect(lambda: [self.handle_go_to("B"), SetStyleSheetForbtn(self.ui, "btn_room_b", "#69ff3d")])
        # self.ui.btn_room_c.clicked.connect(lambda: [self.handle_go_to("C"), SetStyleSheetForbtn(self.ui, "btn_room_c", "#69ff3d")])
        # self.ui.btn_room_d.clicked.connect(lambda: [self.handle_go_to("D"), SetStyleSheetForbtn(self.ui, "btn_room_d", "#69ff3d")])

        self.ui.btn_room_a.clicked.connect(lambda: [self.start_navigation("A"), SetStyleSheetForbtn(self.ui, "btn_room_a", "#69ff3d"), self.inactivity_timer.stop(), self.ui.btn_home_navi.setEnabled(False)])
        self.ui.btn_room_b.clicked.connect(lambda: [self.start_navigation("B"), SetStyleSheetForbtn(self.ui, "btn_room_b", "#69ff3d"), self.inactivity_timer.stop(), self.ui.btn_home_navi.setEnabled(False)])
        self.ui.btn_room_c.clicked.connect(lambda: [self.start_navigation("C"), SetStyleSheetForbtn(self.ui, "btn_room_c", "#69ff3d"), self.inactivity_timer.stop(), self.ui.btn_home_navi.setEnabled(False)])
        self.ui.btn_room_d.clicked.connect(lambda: [self.start_navigation("D"), SetStyleSheetForbtn(self.ui, "btn_room_d", "#69ff3d"), self.inactivity_timer.stop(), self.ui.btn_home_navi.setEnabled(False)])

    def handle_micro(self):
        if self.micro_loop == False:
            self.micro_loop = True
            self.silent_count = 0
            self.listen()

    def listen(self):
        SetStyleSheetForbtn(self.ui, "btn_micro", "#69ff3d")  
        SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff")  
        self.reset_inactivity_timer()
        self.ui.prompt_qna.setText("Listening...")
        self.ui.btn_micro.setEnabled(True)
        self.listen_thread = ListenThread()
        self.listen_thread.finished.connect(self.get_response)
        self.listen_thread.finished.connect(lambda: [self.cleanup_thread(self.listen_thread), self.ui.btn_micro.setEnabled(False), SetStyleSheetForbtn(self.ui, "btn_micro", "#ffffff"), SetStyleSheetForbtn(self.ui, "btn_speaker", "#69ff3d")])
        self.listen_thread.start()

    def get_response(self, query: str):
        self.query = query.lower()  
        if not self.query:
            self.continue_conversation()
        elif self.query == "Are you still there?" or self.query == "Hmm, I didn't quite catch that. Could you please repeat?" or self.query == "Something went wrong while listening." or self.query == "Speech service is unavailable.":
            print(f"AIko: {query}")
            self.ui.prompt_qna.setText(self.query)
            self.silent_count += 1
            if self.silent_count >= 3:
                self.ui.prompt_qna.setText("No response detected. Returning to main menu.")
                self.micro_loop = False
                self.go_to_main_page()
            else:
                self.speak_thread = SpeakThread(self.query)
                self.speak_thread.finished.connect(lambda: [self.cleanup_thread(self.speak_thread), self.listen()])
                self.speak_thread.start()
        else:
            self.response_thread = ResponseThread(self.query, intial_context=initial_context)
            self.response_thread.finished.connect(self.answer)
            self.response_thread.finished.connect(lambda: self.cleanup_thread(self.response_thread))
            self.response_thread.start()

    def answer(self, text: str):
        #self.ui.btn_speaker.setEnabled(True)
        #SetStyleSheetForbtn(self.ui, "btn_speaker", "#69ff3d")
        self.ui.btn_micro.setEnabled(False)
        self.reset_inactivity_timer()
        self.ui.prompt_qna.setText(text)
        # self.ui.prompt_qna.setText("Answering...")
        if text == "You're welcome. Goodbye.":
            print(f"AIko: {text}")
            self.speak_thread = SpeakThread(text)
            self.speak_thread.finished.connect(lambda: [self.cleanup_thread(self.speak_thread), self.ui.btn_home_qna.setEnabled(True), self.ui.btn_micro.setEnabled(True), SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff")])
            self.speak_thread.start()
            # self.btn_speaker_timer.start(4000)
            self.micro_loop = False
        else:
            print(f"AIko: {text}")
            self.speak_thread = SpeakThread(text)
            self.speak_thread.finished.connect(self.continue_conversation)
            self.speak_thread.finished.connect(lambda: self.cleanup_thread(self.speak_thread))
            self.speak_thread.start()

    def continue_conversation(self):
        self.ui.btn_micro.setEnabled(True)
        self.listen()

    def start_navigation(self, room: str):
        if room == self.current_room:
            self.ui.prompt_navi.setText("You are already here!!!")
            self.speak_thread = SpeakThread("AIko You are already here!!!")
            self.speak_thread.finished.connect(lambda: [self.cleanup_thread(self.speak_thread), self.set_color_btn_room("#ffffff"), self.ui.btn_home_navi.setEnabled(True), self.reset_inactivity_timer(), self.ui.prompt_navi.setText("Where do you want to go?")])
            self.speak_thread.start()
            return

        self._set_navigation_buttons_enabled(False)
        self.speak_thread = SpeakThread(f"Let's move to room {room}")
        self.speak_thread.finished.connect(lambda: [_animate_prompt(base_text=f"Heading to room {room}",
                                                                        label_widget=self.ui.prompt_navi,
                                                                        duration_ms=10000,  
                                                                        callback_after=lambda: self._arrive_at(room))])
        self.speak_thread.start()

    def _arrive_at(self, room: str):
        self.current_room = room
        self.speak_thread = SpeakThread(f"We have arrived at room {room}")
        self.speak_thread.finished.connect(lambda: [self.ui.btn_home_navi.setEnabled(True), self._set_navigation_buttons_enabled(True), self.ui.prompt_navi.setText(f"Arrived at room {room}. Ready for next destination."), self.set_color_btn_room("#ffffff")])
        self.reset_inactivity_timer()
        self.speak_thread.start()
        # # Tự động quay về main sau 5 giây
        # QTimer.singleShot(10000, self.go_to_main_page)        

    def on_robot_status_update(self, location):
        if self.mqtt_handler.current_target == location:
            self.ui.prompt_navi.setText(f"Arrived at room {location}. Ready for next destination.")
            # Tự động quay về main sau 10 giây
            QTimer.singleShot(10000, self.go_home)

    def handle_go_to(self, room):
        if self.mqtt_handler.current_position == room:
            self.ui.prompt_navi.setText("You are already here!!!")
        else:
            self._set_navigation_buttons_enabled(False)
            _animate_prompt(
                base_text=f"Heading to room {room}",
                label_widget=self.ui.prompt_navi,
                duration_ms=5000,  # mô phỏng thời gian di chuyển
        )
            self.mqtt_handler.send_destination(room)

    def _set_navigation_buttons_enabled(self, enabled: bool):
        # self.ui.btn_micro.setEnabled(enabled)
        self.ui.btn_room_a.setEnabled(enabled)
        self.ui.btn_room_b.setEnabled(enabled)
        self.ui.btn_room_c.setEnabled(enabled)
        self.ui.btn_room_d.setEnabled(enabled)

    def go_to_main_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)
        SetStyleSheetForbtn(self.ui, "btn_micro", "#ffffff")
        SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff")
        SetStyleSheetForbtn(self.ui, "btn_room_a", "ffffff")
        SetStyleSheetForbtn(self.ui, "btn_room_b", "ffffff")
        SetStyleSheetForbtn(self.ui, "btn_room_c", "ffffff")
        SetStyleSheetForbtn(self.ui, "btn_room_d", "ffffff")
        self.ui.btn_home_navi.setEnabled(True)

    def reset_inactivity_timer(self):
        self.inactivity_timer.stop()
        self.inactivity_timer.start()



    def handle_btn_qna(self):
        SetStyleSheetForbtn(self.ui, "btn_speaker", "#69ff3d")
        self.welcome_thread = WelcomeThread()
        self.welcome_thread.finished.connect(lambda: [self.cleanup_thread(self.welcome_thread), self.ui.btn_home_qna.setEnabled(True), self.ui.btn_micro.setEnabled(True), SetStyleSheetForbtn(self.ui, "btn_speaker", "#ffffff")])
        self.welcome_thread.start()

    def handle_btn_navi(self):
        self.speak_thread = SpeakThread("Where do you want to go?")
        self.speak_thread.finished.connect(lambda: [self.cleanup_thread(self.speak_thread), self.ui.btn_room_a.setEnabled(True), self.ui.btn_room_b.setEnabled(True), self.ui.btn_room_c.setEnabled(True), self.ui.btn_room_d.setEnabled(True), self.ui.btn_home_navi.setEnabled(True)])
        self.speak_thread.start()

    def set_color_btn_room(self, color):
        SetStyleSheetForbtn(self.ui, "btn_room_a", color)
        SetStyleSheetForbtn(self.ui, "btn_room_b", color)
        SetStyleSheetForbtn(self.ui, "btn_room_c", color)
        SetStyleSheetForbtn(self.ui, "btn_room_d", color)

    def cleanup_thread(self, thread):
        if thread is not None:
            thread.quit()
            thread.wait()
            thread.deleteLater()
            thread = None



if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    # widget.resize(1920, 1080)
    screen = QApplication.primaryScreen()
    size = screen.availableGeometry().size()
    widget.resize(size.width(), size.height())
    widget.show()
    sys.exit(app.exec())