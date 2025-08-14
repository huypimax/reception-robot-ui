import sys
from ui.main_ui import Ui_MainWindow
from ui.resources.font_configurator import apply_custom_fonts
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsDropShadowEffect
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor

from mqtt_client import MQTTHandler
import asyncio
import os
from welcome_thread import WelcomeThread
from speak_thread import SpeakThread
from listen_thread import ListenThread
from response_thread import ResponseThread
from call_chatbot import AIkoBot
from ui.web import WebTab


ASSISTANT_NAME = "AIko"
initial_context = [
            {"role": "user", "parts": [{"text": "You are a helpful, concise virtual assistant named AIko, created by Fablab."}]},
            {"role": "model", "parts": [{"text": "Understood. I'm AIko, created by Fablab."}]},
            {"role": "user", "parts": [{"text": "When answering, use 1–2 full sentences, clear and friendly tone. No bullet points or keywords only."}]},
            {"role": "model", "parts": [{"text": "Okay. I will respond in short, clear sentences."}]}
        ]
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        apply_custom_fonts(self.ui)

        self.current_room = ""
        self.micro_loop = False
        self.silent_count = 0

        self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)
        self.applyShadow([self.ui.btn_qna, self.ui.btn_home_qna, self.ui.btn_navi, self.ui.btn_home_navi, self.ui.btn_about_us, self.ui.btn_home_about_us, self.ui.btn_micro, self.ui.btn_speaker, self.ui.widget,
                          self.ui.widget_12, self.ui.widget_7, self.ui.widget_19, self.ui.widget_18, self.ui.btn_room_a, self.ui.btn_room_b, self.ui.btn_room_c, self.ui.btn_room_d,
                          self.ui.label_6, self.ui.label_7, self.ui.label_8, self.ui.label_9, self.ui.label_19, self.ui.label_20])

        self.web_ = WebTab(self.ui)
        # self.mqtt_handler = MQTTHandler(self.on_robot_status_update)
        # self.bot = AIkoBot()

        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(40000)  
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.go_to_main_page)

        # --- Logic điều hướng ---

        self.ui.btn_qna.clicked.connect(lambda: [self.handle_btn_qna(), self.ui.stackedWidget.setCurrentWidget(self.ui.page_qna), self.ui.prompt_qna.setText("Press the microphone button to start a conversation."), self.reset_inactivity_timer(), self.ui.btn_home_qna.setEnabled(False), self.ui.btn_micro.setEnabled(False)])
        self.ui.btn_navi.clicked.connect(lambda: [self.handle_btn_navi(), self.ui.stackedWidget.setCurrentWidget(self.ui.page_navi), self.reset_inactivity_timer(), self.ui.btn_home_navi.setEnabled(False), self._set_navigation_buttons_enabled(False), self.set_color_btn_room("#ffffff"), self.ui.prompt_navi.setText("Where do you want to go?")])
        self.ui.btn_about_us.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page))
        self.ui.btn_home_qna.clicked.connect(lambda: self.go_to_main_page())
        self.ui.btn_home_navi.clicked.connect(lambda: self.go_to_main_page())
        self.ui.btn_home_about_us.clicked.connect(lambda: self.go_to_main_page())
        

        self.ui.btn_micro.clicked.connect(lambda: [self.handle_micro(), self.ui.btn_home_qna.setEnabled(False)])
        #self.ui.btn_speaker.setEnabled(False)

        # self.ui.btn_room_a.clicked.connect(lambda: [self.handle_go_to("A"), self.SetStyleSheetForbtn("btn_room_a", "#69ff3d")])
        # self.ui.btn_room_b.clicked.connect(lambda: [self.handle_go_to("B"), self.SetStyleSheetForbtn("btn_room_b", "#69ff3d")])
        # self.ui.btn_room_c.clicked.connect(lambda: [self.handle_go_to("C"), self.SetStyleSheetForbtn("btn_room_c", "#69ff3d")])
        # self.ui.btn_room_d.clicked.connect(lambda: [self.handle_go_to("D"), self.SetStyleSheetForbtn("btn_room_d", "#69ff3d")])

        self.ui.btn_room_a.clicked.connect(lambda: [self.start_navigation("A"), self.SetStyleSheetForbtn("btn_room_a", "#69ff3d"), self.inactivity_timer.stop(), self.ui.btn_home_navi.setEnabled(False)])
        self.ui.btn_room_b.clicked.connect(lambda: [self.start_navigation("B"), self.SetStyleSheetForbtn("btn_room_b", "#69ff3d"), self.inactivity_timer.stop(), self.ui.btn_home_navi.setEnabled(False)])
        self.ui.btn_room_c.clicked.connect(lambda: [self.start_navigation("C"), self.SetStyleSheetForbtn("btn_room_c", "#69ff3d"), self.inactivity_timer.stop(), self.ui.btn_home_navi.setEnabled(False)])
        self.ui.btn_room_d.clicked.connect(lambda: [self.start_navigation("D"), self.SetStyleSheetForbtn("btn_room_d", "#69ff3d"), self.inactivity_timer.stop(), self.ui.btn_home_navi.setEnabled(False)])

    def handle_micro(self):
        if self.micro_loop == False:
            self.micro_loop = True
            self.silent_count = 0
            self.listen()

    def listen(self):
        self.SetStyleSheetForbtn("btn_micro", "#69ff3d")  
        self.SetStyleSheetForbtn("btn_speaker", "#ffffff")  
        self.reset_inactivity_timer()
        self.ui.prompt_qna.setText("Listening...")
        self.ui.btn_micro.setEnabled(True)
        self.listen_thread = ListenThread()
        self.listen_thread.finished.connect(self.get_response)
        self.listen_thread.finished.connect(lambda: [self.cleanup_thread(self.listen_thread), self.ui.btn_micro.setEnabled(False), self.SetStyleSheetForbtn("btn_micro", "#ffffff"), self.SetStyleSheetForbtn("btn_speaker", "#69ff3d")])
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
                self.speak_thread = SpeakThread("AIko" + self.query)
                self.speak_thread.finished.connect(lambda: [self.cleanup_thread(self.speak_thread), self.listen()])
                self.speak_thread.start()
        else:
            self.response_thread = ResponseThread(self.query, intial_context=initial_context)
            self.response_thread.finished.connect(self.answer)
            self.response_thread.finished.connect(lambda: self.cleanup_thread(self.response_thread))
            self.response_thread.start()

    def answer(self, text: str):
        #self.ui.btn_speaker.setEnabled(True)
        #self.SetStyleSheetForbtn("btn_speaker", "#69ff3d")
        self.ui.btn_micro.setEnabled(False)
        self.reset_inactivity_timer()
        self.ui.prompt_qna.setText(text)
        # self.ui.prompt_qna.setText("Answering...")
        if text == "You're welcome. Goodbye.":
            print(f"AIko: {text}")
            self.speak_thread = SpeakThread("AIko" + text)
            self.speak_thread.finished.connect(lambda: [self.cleanup_thread(self.speak_thread), self.ui.btn_home_qna.setEnabled(True), self.ui.btn_micro.setEnabled(True), self.SetStyleSheetForbtn("btn_speaker", "#ffffff")])
            self.speak_thread.start()
            # self.btn_speaker_timer.start(4000)
            self.micro_loop = False
        else:
            print(f"AIko: {text}")
            self.speak_thread = SpeakThread("AIko" + text)
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
        self.speak_thread = SpeakThread(f"AIko Let's move to room {room}")
        self.speak_thread.finished.connect(lambda: [self._animate_prompt(base_text=f"Heading to room {room}",
                                                                        label_widget=self.ui.prompt_navi,
                                                                        duration_ms=10000,  
                                                                        callback_after=lambda: self._arrive_at(room))])
        self.speak_thread.start()

    def _arrive_at(self, room: str):
        self.current_room = room
        self.speak_thread = SpeakThread(f"AIko We have arrived at room {room}")
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
            self._animate_prompt(
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
        self.SetStyleSheetForbtn("btn_micro", "#ffffff")
        self.SetStyleSheetForbtn("btn_speaker", "#ffffff")
        self.SetStyleSheetForbtn("btn_room_a", "ffffff")
        self.SetStyleSheetForbtn("btn_room_b", "ffffff")
        self.SetStyleSheetForbtn("btn_room_c", "ffffff")
        self.SetStyleSheetForbtn("btn_room_d", "ffffff")
        self.ui.btn_home_navi.setEnabled(True)

    def reset_inactivity_timer(self):
        self.inactivity_timer.stop()
        self.inactivity_timer.start()


    def _animate_prompt(self, base_text: str, label_widget, duration_ms, callback_after=None):
        """
        Hiệu ứng động "..." sau base_text
        """
        dots = [".", "..", "..."]
        index = 0
        timer = QTimer(self)

        def update():
            nonlocal index
            label_widget.setText(f"{base_text}{dots[index]}")
            index = (index + 1) % len(dots)

        timer.timeout.connect(update)
        timer.start(500)  # mỗi 500ms update chấm

        # Sau duration_ms thì stop hiệu ứng và gọi callback nếu có
        QTimer.singleShot(duration_ms, lambda: (timer.stop(), callback_after() if callback_after else None))

    def applyShadow(self, objects, blur=20, x_offset=4, y_offset=4, color=QColor(0, 0, 0, 150)):
        """Áp dụng hiệu ứng bóng cho danh sách các đối tượng"""
        for obj in objects:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(blur)
            shadow.setXOffset(x_offset)
            shadow.setYOffset(y_offset)
            shadow.setColor(color)
            obj.setGraphicsEffect(shadow)

    def handle_btn_qna(self):
        self.SetStyleSheetForbtn("btn_speaker", "#69ff3d")
        self.welcome_thread = WelcomeThread()
        self.welcome_thread.finished.connect(lambda: [self.cleanup_thread(self.welcome_thread), self.ui.btn_home_qna.setEnabled(True), self.ui.btn_micro.setEnabled(True), self.SetStyleSheetForbtn("btn_speaker", "#ffffff")])
        self.welcome_thread.start()

    def handle_btn_navi(self):
        self.speak_thread = SpeakThread("Where do you want to go?")
        self.speak_thread.finished.connect(lambda: [self.cleanup_thread(self.speak_thread), self.ui.btn_room_a.setEnabled(True), self.ui.btn_room_b.setEnabled(True), self.ui.btn_room_c.setEnabled(True), self.ui.btn_room_d.setEnabled(True), self.ui.btn_home_navi.setEnabled(True)])
        self.speak_thread.start()

    def set_color_btn_room(self, color):
        self.SetStyleSheetForbtn("btn_room_a", color)
        self.SetStyleSheetForbtn("btn_room_b", color)
        self.SetStyleSheetForbtn("btn_room_c", color)
        self.SetStyleSheetForbtn("btn_room_d", color)

    def SetStyleSheetForbtn(self, btn, background_color, text_color="black", hover_background="#ffffff"):
        button = getattr(self.ui, btn)
        button.setStyleSheet(f"""
            QPushButton#{btn} {{
                border-radius: 30px;
                border-color: white;
                background-color: {background_color};
                color: {text_color};
                text-align: center;
                font-family: Inter, sans-serif;
            }}

            QPushButton#{btn}:hover {{
                background-color: {hover_background};
            }}

            QPushButton#{btn}:pressed {{
                padding-left: 5px;
                padding-top: 5px;
            }}
        """)


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