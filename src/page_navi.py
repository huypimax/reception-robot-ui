from PyQt6.QtCore import QTimer, QThread
from ui.widget_conf.ui_utils import SetStyleSheetForbtn, _animate_prompt, set_color_btn_room, _set_navigation_buttons_enabled
from ui.main_ui import Ui_MainWindow
from pathplanning import LocationManager, ArrivalManager
from thread_speak import SpeakThread
from thread_speak_new import SpeakManager

class NaviPage:
    def __init__(self, main: Ui_MainWindow):
        self.ui = main
        self.speaker = SpeakManager()
        self.arrival_manager = ArrivalManager(self.ui)
        self.arrival_manager.start_arrival_subscriber()
        self.location_manager = LocationManager(self.ui, self.arrival_manager)
        self.location_manager.start_location_subscriber()
        self.current_place = ""

        self.place_button_pairs = [
            ("Water intake", "btn_room_a"),
            ("Chemistry hall", "btn_room_b"),  
            ("Restroom", "btn_room_c"),
            ("Stairs", "btn_room_d"), 
            ("Robotics lab", "btn_room_e"), 
            ("Electrical lab", "btn_room_f"),
        ]

        # Dictionary
        self.place_to_button_map = {place: btn_name for place, btn_name in self.place_button_pairs}

        # connect button 
        for place, btn_name in self.place_button_pairs:
            button = getattr(self.ui, btn_name)  # Lấy button object từ tên
            button.setText(f"{place}")
            button.clicked.connect(lambda checked=False, p=place, b=btn_name: [
                self.start_navigation(p, b),
                SetStyleSheetForbtn(self.ui, b, "#69ff3d")
                ])      

        self.ui.btn_home_navi.clicked.connect(lambda: self.go_to_main_page())
        
    def handle_btn_navi(self):
        self.ui.prompt_navi.setText("Where do you want to go")
        self.speaker.say("Where do you want to go?")
        self.speaker.connect_finished(lambda: [
            self.ui.btn_home_navi.setEnabled(True),
            _set_navigation_buttons_enabled(self.ui, True)  # Enable tất cả button từ pairs
        ])
         
    def start_navigation(self, place: str, btn_name: str):
        self.ui.btn_home_navi.setEnabled(False)
        _set_navigation_buttons_enabled(self.ui, False)

        if place == self.current_place:
            if btn_name is None:
                print(f"Error: btn_name is None for place '{place}'")
                return
            self.ui.prompt_navi.setText("You are already here!!!")
            self.speaker.say("You are already here!!!")
            self.speaker.connect_finished(lambda: [
                SetStyleSheetForbtn(self.ui, btn_name, "#ffffff"),
                self.ui.btn_home_navi.setEnabled(True),
                self.ui.btn_home_navi.setEnabled(True),
                self.ui.prompt_navi.setText("Where do you want to go?")
            ])
            return

        self.location_manager.send_goal(place) 
        SetStyleSheetForbtn(self.ui, btn_name, "#69ff3d")

        # Dọn kết nối cũ
        try:
            self.arrival_manager.subscriber_thread.arrival_update.disconnect()
        except TypeError:
            pass

        self.speaker.say(f"Let's move to {place}")
        self.speaker.connect_finished(lambda:[_set_navigation_buttons_enabled(self.ui, False),
                                              self.ui.btn_home_navi.setEnabled(False)])
        
        if self.current_place != place:
            self.stop_prompt = _animate_prompt(
                base_text=f"Heading to {place}",
                label_widget=self.ui.prompt_navi
            )
        
        self.arrival_manager.subscriber_thread.arrival_update.connect(
            lambda arrived, p=place, b=btn_name: self._arrive_at(arrived, p, b)
        )


    def _arrive_at(self, arrived: bool, place: str, btn_name: str):
        if arrived:
            # Dừng animation nếu đang chạy
            if hasattr(self, "stop_prompt") and self.stop_prompt:
                self.stop_prompt()
                self.stop_prompt = None

            self.current_place = place
            if btn_name is None:
                print(f"Error: btn_name is None for place '{place}'")
                return

            self.speaker.say(f"We have arrived at {place}")
            self.speaker.connect_finished(lambda: [
                self.ui.btn_home_navi.setEnabled(True),
                _set_navigation_buttons_enabled(self.ui, True),
                self.ui.prompt_navi.setText(f"Arrived at {place}. Ready for next destination."),
                SetStyleSheetForbtn(self.ui, btn_name, "#ffffff")
            ])


    def go_to_main_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)
        self.ui.prompt_navi.setText("Where do you want to go")

    def cleanup_thread(self, thread: QThread):
        if thread is not None:
            thread.quit()
            thread.wait()
            thread.deleteLater()
            thread = None