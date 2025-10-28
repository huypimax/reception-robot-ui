from PyQt6.QtCore import QTimer, QThread
from ui.widget_conf.ui_utils import SetStyleSheetForbtn, _animate_prompt
from ui.main_ui import Ui_MainWindow
from pathplanning import LocationManager
from thread_speak import SpeakThread

class NaviPage:
    def __init__(self, main: Ui_MainWindow):
        self.ui = main
        self.location_manager = LocationManager(self.ui)
        self.current_place = ""

        self.place_button_pairs = [
            ("Electrical lab", "btn_room_a"), 
            ("Robotics lab", "btn_room_b"), 
            ("Chemistry Hall", "btn_room_c"),  
            ("Man restroom", "btn_room_d") 
        ]

        # Dictionary
        self.place_to_button_map = {place: btn_name for place, btn_name in self.place_button_pairs}

        # connect button 
        for place, btn_name in self.place_button_pairs:
            button = getattr(self.ui, btn_name)  # Lấy button object từ tên
            button.setText(f"{place}")
            button.clicked.connect(lambda checked=False, p=place, b=btn_name: [
                self.start_navigation(p, b), 
                SetStyleSheetForbtn(self.ui, b, "#69ff3d"), 
                ])      

        self.ui.btn_home_navi.clicked.connect(lambda: self.go_to_main_page())
        
    def handle_btn_navi(self):
        self.speak_thread = SpeakThread("Where do you want to go?")
        self.speak_thread.finished.connect(lambda: [
            self.ui.btn_home_navi.setEnabled(True),
            self._set_navigation_buttons_enabled(True)  # Enable tất cả button từ pairs
        ])
        self.speak_thread.start()

    def start_navigation(self, place: str, btn_name: str):
        self.ui.btn_home_navi.setEnabled(False)
        if place == self.current_place:
            if btn_name is None:  # Kiểm tra để tránh lỗi
                print(f"Error: btn_name is None for place '{place}'")
                return

            self.ui.prompt_navi.setText("You are already here!!!")
            self.speak_thread = SpeakThread("You are already here!!!")
            self.speak_thread.finished.connect(lambda: [self.cleanup_thread(self.speak_thread), 
                                                        SetStyleSheetForbtn(self.ui, btn_name, "#ffffff"), 
                                                        self.ui.btn_home_navi.setEnabled(True), 
                                                        self.ui.prompt_navi.setText("Where do you want to go?")])
            self.speak_thread.start()
            return

        self.location_manager.send_waypoint(place)
        self._set_navigation_buttons_enabled(False)
        self.speak_thread = SpeakThread(f"Let's move to {place}")
        self.speak_thread.finished.connect(lambda checked=False, p=place, b=btn_name: [
            _animate_prompt(base_text=f"Heading to {p}",
                            label_widget=self.ui.prompt_navi,
                            duration_ms=10000,  
                            callback_after=lambda cchecked=False, pp=p, bb=b: self._arrive_at(pp, bb))
            ])  # Capture p và b
        self.speak_thread.start()

    def _arrive_at(self, place: str, btn_name: str):
        self.current_place = place
        if btn_name is None:  # Kiểm tra để tránh lỗi
            print(f"Error: btn_name is None for place '{place}'")
            return

        self.speak_thread = SpeakThread(f"We have arrived at {place}")
        self.speak_thread.finished.connect(lambda: [self.ui.btn_home_navi.setEnabled(True), 
                                                    self._set_navigation_buttons_enabled(True), 
                                                    self.ui.prompt_navi.setText(f"Arrived at {place}. Ready for next destination."), 
                                                    SetStyleSheetForbtn(self.ui, btn_name, "#ffffff")])
        self.speak_thread.start()

    def _set_navigation_buttons_enabled(self, enabled: bool):
        # self.ui.btn_micro.setEnabled(enabled)
        for place, btn_name in self.place_button_pairs:
            button = getattr(self.ui, btn_name)  # Lấy button object từ tên
            button.setEnabled(enabled)

    def go_to_main_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)

    def cleanup_thread(self, thread: QThread):
        if thread is not None:
            thread.quit()
            thread.wait()
            thread.deleteLater()
            thread = None