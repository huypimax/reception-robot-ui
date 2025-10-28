from PyQt6.QtCore import QTimer
from PyQt6.QtCore import QThread
from ui.widget_conf.ui_utils import SetStyleSheetForbtn, _animate_prompt
from ui.main_ui import Ui_MainWindow
from thread_speak import SpeakThread

class NaviPage:
    def __init__(self, main: Ui_MainWindow, inactivity_timer: QTimer):
        self.ui = main
        self.inactivity_timer = inactivity_timer
        self.current_place = ""
        self.ui.btn_home_navi.clicked.connect(lambda: self.go_to_main_page())
        self.ui.btn_room_a.clicked.connect(lambda: [self.start_navigation("A"), SetStyleSheetForbtn(self.ui, "btn_room_a", "#69ff3d"), self.inactivity_timer.stop(), self.ui.btn_home_navi.setEnabled(False)])
        self.ui.btn_room_b.clicked.connect(lambda: [self.start_navigation("B"), SetStyleSheetForbtn(self.ui, "btn_room_b", "#69ff3d"), self.inactivity_timer.stop(), self.ui.btn_home_navi.setEnabled(False)])
        self.ui.btn_room_c.clicked.connect(lambda: [self.start_navigation("C"), SetStyleSheetForbtn(self.ui, "btn_room_c", "#69ff3d"), self.inactivity_timer.stop(), self.ui.btn_home_navi.setEnabled(False)])
        self.ui.btn_room_d.clicked.connect(lambda: [self.start_navigation("D"), SetStyleSheetForbtn(self.ui, "btn_room_d", "#69ff3d"), self.inactivity_timer.stop(), self.ui.btn_home_navi.setEnabled(False)])

    def handle_btn_navi(self):
        self.speak_thread = SpeakThread("Where do you want to go?")
        self.speak_thread.finished.connect(lambda: [
            self.ui.btn_room_a.setEnabled(True), self.ui.btn_room_b.setEnabled(True),
            self.ui.btn_room_c.setEnabled(True), self.ui.btn_room_d.setEnabled(True)
        ])
        self.speak_thread.start()

    def start_navigation(self, place: str):
        if place == self.current_place:
            btn_name = f"btn_room_{place.lower()}"  
            self.ui.prompt_navi.setText("You are already here!!!")
            self.speak_thread = SpeakThread("You are already here!!!")
            self.speak_thread.finished.connect(lambda: [self.cleanup_thread(self.speak_thread), SetStyleSheetForbtn(self.ui, btn_name, "#ffffff"), self.ui.btn_home_navi.setEnabled(True), self.reset_inactivity_timer(), self.ui.prompt_navi.setText("Where do you want to go?")])
            self.speak_thread.start()
            return

        self._set_navigation_buttons_enabled(False)
        self.speak_thread = SpeakThread(f"Let's move to place {place}")
        self.speak_thread.finished.connect(lambda: [_animate_prompt(base_text=f"Heading to {place}",
                                                                    label_widget=self.ui.prompt_navi,
                                                                    duration_ms=10000,  
                                                                    callback_after=lambda: self._arrive_at(place))])
        self.speak_thread.start()

    def _arrive_at(self, place: str):
        self.current_place = place
        btn_name = f"btn_room_{place.lower()}"  
        self.speak_thread = SpeakThread(f"We have arrived at {place}")
        self.speak_thread.finished.connect(lambda: [self.ui.btn_home_navi.setEnabled(True), self._set_navigation_buttons_enabled(True), self.ui.prompt_navi.setText(f"Arrived at {place}. Ready for next destination."), SetStyleSheetForbtn(self.ui, btn_name, "#ffffff")])
        self.reset_inactivity_timer()
        self.speak_thread.start()

    def _set_navigation_buttons_enabled(self, enabled: bool):
        # self.ui.btn_micro.setEnabled(enabled)
        self.ui.btn_room_a.setEnabled(enabled)
        self.ui.btn_room_b.setEnabled(enabled)
        self.ui.btn_room_c.setEnabled(enabled)
        self.ui.btn_room_d.setEnabled(enabled)

    def reset_inactivity_timer(self):
        self.inactivity_timer.stop()
        self.inactivity_timer.start()

    def go_to_main_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)

    def cleanup_thread(self, thread: QThread):
        if thread is not None:
            thread.quit()
            thread.wait()
            thread.deleteLater()
            thread = None
