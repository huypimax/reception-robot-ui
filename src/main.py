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

ASSISTANT_NAME = "AIko"

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        apply_custom_fonts(self.ui)

        self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)
        self.applyShadow([self.ui.btn_qna, self.ui.btn_navi, self.ui.btn_micro, self.ui.btn_speaker,
                          self.ui.btn_room_a, self.ui.btn_room_b, self.ui.btn_room_c, self.ui.btn_room_d, self.ui.widget,
                          self.ui.widget_12, self.ui.widget_7, self.ui.btn_home_qna, self.ui.btn_home_navi])

        #self.mqtt_handler = MQTTHandler(self.on_robot_status_update)
        #self.bot = AIkoBot()
        self.current_room = None
        self.is_listening = False

        self.btn_speaker_timer = QTimer()
        self.btn_speaker_timer.setSingleShot(True)
        self.btn_speaker_timer.timeout.connect(lambda: self.SetStyleSheetForbtn("btn_speaker", "#ffffff")) 
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(20000)  
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.go_to_main_page)

        # --- Logic điều hướng ---

        self.ui.btn_qna.clicked.connect(lambda: [self.handle_btn_qna(), self.ui.stackedWidget.setCurrentWidget(self.ui.page_qna), self.reset_inactivity_timer(), self.ui.prompt_qna.setText("Press the microphone button to start a conversation."), self.ui.btn_micro.setEnabled(False)])
        self.ui.btn_navi.clicked.connect(lambda: [self.handle_btn_navi(), self.ui.stackedWidget.setCurrentWidget(self.ui.page_navi), self.reset_inactivity_timer()])
        self.ui.btn_home_qna.clicked.connect(lambda: self.go_to_main_page())
        self.ui.btn_home_navi.clicked.connect(lambda: self.go_to_main_page())

        self.ui.btn_micro.clicked.connect(lambda: [self.on_micro_clicked(), self.reset_inactivity_timer(), self.ui.btn_home_qna.setEnabled(True)])
        #self.ui.btn_speaker.setEnabled(False)

        # self.ui.btn_room_a.clicked.connect(lambda: [self.handle_go_to("A"), self.SetStyleSheetForbtn("btn_room_a", "#69ff3d")])
        # self.ui.btn_room_b.clicked.connect(lambda: [self.handle_go_to("B"), self.SetStyleSheetForbtn("btn_room_b", "#69ff3d")])
        # self.ui.btn_room_c.clicked.connect(lambda: [self.handle_go_to("C"), self.SetStyleSheetForbtn("btn_room_c", "#69ff3d")])
        # self.ui.btn_room_d.clicked.connect(lambda: [self.handle_go_to("D"), self.SetStyleSheetForbtn("btn_room_d", "#69ff3d")])

        self.ui.btn_room_a.clicked.connect(lambda: [self.start_navigation("A"), self.SetStyleSheetForbtn("btn_room_a", "#69ff3d")])
        self.ui.btn_room_b.clicked.connect(lambda: [self.start_navigation("B"), self.SetStyleSheetForbtn("btn_room_b", "#69ff3d")])
        self.ui.btn_room_c.clicked.connect(lambda: [self.start_navigation("C"), self.SetStyleSheetForbtn("btn_room_c", "#69ff3d")])
        self.ui.btn_room_d.clicked.connect(lambda: [self.start_navigation("D"), self.SetStyleSheetForbtn("btn_room_d", "#69ff3d")])

    def on_micro_clicked(self):
        self.stop_all_threads()
        self.is_listening = False
        self.ui.prompt_qna.setText("🎤 Cancelled.")
        self.SetStyleSheetForbtn("btn_micro", "#ffffff")
        self.ui.btn_home_qna.setEnabled(True)

        # Tiếp tục lắng nghe lại
        self.handle_micro()

    def handle_micro(self):
        # Dọn dẹp listen_thread nếu có
        # old_thread = getattr(self, "listen_thread", None)
        # if old_thread:
        #     self.cleanup_thread(old_thread)
        self.SetStyleSheetForbtn("btn_micro", "#69ff3d")  
        self.SetStyleSheetForbtn("btn_speaker", "#ffffff")  
        self.ui.prompt_qna.setText("Listening...")
        self.listen_thread = ListenThread()
        self.listen_thread.finished.connect(self.get_response)
        self.listen_thread.finished.connect(lambda: self.cleanup_thread(self.listen_thread))
        self.listen_thread.start()

    def get_response(self, query: str):
        self.SetStyleSheetForbtn("btn_micro", "#ffffff")  
        self.SetStyleSheetForbtn("btn_speaker", "#69ff3d")
        if not query:
            self.continue_conversation()
        else:
            self.response_thread = ResponseThread(query)
            self.response_thread.finished.connect(self.answer)
            self.response_thread.finished.connect(lambda: self.cleanup_thread(self.response_thread))
            self.response_thread.start()

    def answer(self, text: str):
        #self.ui.btn_speaker.setEnabled(True)
        #self.SetStyleSheetForbtn("btn_speaker", "#69ff3d")
        self.ui.btn_micro.setEnabled(False)
        self.reset_inactivity_timer()
        #self.ui.prompt_qna.setText(text)
        self.ui.prompt_qna.setText("Answering...")
        if text == "You're welcome. Goodbye.":
            print(f"AIko: {text}")
            self.speak_thread = SpeakThread(text)
            self.speak_thread.finished.connect(lambda: self.cleanup_thread(self.speak_thread))
            self.speak_thread.start()
            self.btn_speaker_timer.start(4000) 
            self.ui.btn_home_qna.setEnabled(True)
        else:
            print(f"AIko: {text}")
            self.speak_thread = SpeakThread(text)
            self.speak_thread.finished.connect(self.continue_conversation)
            self.speak_thread.finished.connect(lambda: self.cleanup_thread(self.speak_thread))
            self.speak_thread.start()

    def continue_conversation(self):
        self.ui.btn_micro.setEnabled(True)
        QTimer.singleShot(500, self.handle_micro)

    def start_navigation(self, room: str):
        if room == self.current_room:
            self.ui.prompt_navi.setText("You are already here!!!")
            return

        self._set_navigation_buttons_enabled(False)
        self._animate_prompt(
            base_text=f"Heading to room {room}",
            label_widget=self.ui.prompt_navi,
            duration_ms=5000,  # mô phỏng thời gian di chuyển
            callback_after=lambda: self._arrive_at(room)
        )

    def _arrive_at(self, room: str):
        self.current_room = room
        self._set_navigation_buttons_enabled(True)
        self.ui.prompt_navi.setText(f"Arrived at room {room}. Ready for next destination.")

        # Tự động quay về main sau 5 giây
        # QTimer.singleShot(10000, self.go_home)

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
        self.stop_all_threads()
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)
        self.SetStyleSheetForbtn("btn_micro", "#ffffff")
        self.SetStyleSheetForbtn("btn_speaker", "#ffffff")
        self.SetStyleSheetForbtn("btn_room_a", "#ffffff")
        self.SetStyleSheetForbtn("btn_room_b", "#ffffff")
        self.SetStyleSheetForbtn("btn_room_c", "#ffffff")
        self.SetStyleSheetForbtn("btn_room_d", "#ffffff")

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

    def handle_btn_qna(self):
        # self.ui.btn_home_qna.setEnabled(False)
        self.SetStyleSheetForbtn("btn_speaker", "#69ff3d")
        self.btn_speaker_timer.start(7000)
        self.welcome_thread = WelcomeThread()
        self.welcome_thread.finished.connect(lambda: [self.cleanup_thread(self.welcome_thread), self.ui.btn_home_qna.setEnabled(True), self.ui.btn_micro.setEnabled(True)])
        self.welcome_thread.start()

    def handle_btn_navi(self):
        self.speak_thread = SpeakThread("Where do you want to go?")
        self.speak_thread.finished.connect(lambda: self.cleanup_thread(self.speak_thread))
        self.speak_thread.start()

    def SetStyleSheetForbtn(self, btn, background_color):
        #Style cho nút btnEmployeeWorking
        button = getattr(self.ui, btn)
        button.setStyleSheet(f"""
                QPushButton#{btn} {{
                    border-radius: 15px;
                    border-color: white;
                    background-color: {background_color};  /* Màu nền mới */
                    color: white;
                    text-align: center;
                    font-family: Inter, sans-serif;
                }}

                QPushButton#{btn}:hover {{
                    background-color: #ffffff;  /* Màu nền khi hover */
                }}

                QPushButton#{btn}:pressed {{
                    padding-left: 5px;
                    padding-top: 5px;
                }}
                """)                         
    
    def applyShadow(self, objects, blur=20, x_offset=4, y_offset=4, color=QColor(0, 0, 0, 150)):
        """Áp dụng hiệu ứng bóng cho danh sách các đối tượng"""
        for obj in objects:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(blur)
            shadow.setXOffset(x_offset)
            shadow.setYOffset(y_offset)
            shadow.setColor(color)
            obj.setGraphicsEffect(shadow)

    def cleanup_thread(self, thread):
        if thread is None:
            return
        try:
            if thread.isRunning():
                print("⚠️ Cannot cleanup a running thread directly. It should be stopped via requestInterruption.")
                return  # Tránh xóa thread đang chạy
            thread.deleteLater()
            print("🧹 Thread cleaned up safely.")
        except RuntimeError:
            print("⚠️ Tried to clean up a deleted thread.")

    def stop_all_threads(self):
        # Dừng từng thread an toàn
        self.safe_stop("listen_thread")
        self.safe_stop("response_thread")
        self.safe_stop("speak_thread")
        self.safe_stop("welcome_thread")

    def safe_stop(self, thread_name):
        thread = getattr(self, thread_name, None)
        if thread:
            try:
                if thread.isRunning():
                    print(f"🛑 Stopping {thread_name} ...")
                    thread.requestInterruption()
                    thread.quit()  # Cho thread kết thúc gracefully
                    thread.wait(1000)  # Tối đa 1 giây

                thread.deleteLater()
                print(f"🧹 {thread_name} deleted safely.")
            except RuntimeError:
                print(f"⚠️ {thread_name} was already deleted.")
            finally:
                setattr(self, thread_name, None)


  

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    # widget.resize(1920, 1080)
    screen = QApplication.primaryScreen()
    size = screen.availableGeometry().size()
    widget.resize(size.width(), size.height())
    widget.show()
    sys.exit(app.exec())