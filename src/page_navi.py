from PyQt6.QtCore import QTimer, QThread
from ui.widget_conf.ui_utils import SetStyleSheetForbtn, _animate_prompt, set_color_btn_room, _set_navigation_buttons_enabled
from ui.main_ui import Ui_MainWindow
from pathplanning import LocationManager, ArrivalManager
from thread_speak import SpeakThread
from thread_speak import SpeakManager
from language_manager import get_language_manager, get_string, update_widgets_auto
import utilities.string_ids as stringIds
import utilities.constants as constants
import utilities.colors as colors

class NaviPage:
    def __init__(self, main: Ui_MainWindow):
        self.ui = main
        self.speaker = SpeakManager()
        self.lang_manager = get_language_manager()
        self.arrival_manager = ArrivalManager(self.ui)
        self.arrival_manager.start_arrival_subscriber()
        self.location_manager = LocationManager(self.ui, self.arrival_manager)
        self.location_manager.start_location_subscriber()
        self.current_place = ""

        self.place_translation_map = {
            "Water Intake": stringIds.NAV_ROOM_WATER_INTAKE,
            "Chemistry Hall": stringIds.NAV_ROOM_CHEMISTRY_HALL,
            "Restroom": stringIds.NAV_ROOM_RESTROOM,
            "Stairs": stringIds.NAV_ROOM_STAIRS,
            "Robotics Lab": stringIds.NAV_ROOM_ROBOTICS_LAB,
            "Electrical Lab": stringIds.NAV_ROOM_ELECTRICAL_LAB,
        }
        
        self.place_button_pairs = constants.PLACE_BUTTON_PAIRS

        # Dictionary
        self.place_to_button_map = {place: btn_name for place, btn_name in self.place_button_pairs}

        # connect button 
        self._update_room_buttons()      

        self.ui.btn_home_navi.clicked.connect(lambda: self.go_to_main_page())
        
    def handle_btn_navi(self):
        where_text = get_string(stringIds.NAV_WHERE_TO_GO)
        self.ui.prompt_navi.setText(where_text)
        self.speaker.say(get_string(stringIds.NAV_WHERE_TO_GO_QUESTION))
        self.speaker.connect_finished(lambda: [
            self.ui.btn_home_navi.setEnabled(True),
            _set_navigation_buttons_enabled(self.ui, True)  # Enable tất cả button từ pairs
        ])
         
    def _get_translated_place(self, place: str) -> str:
        translation_key = self.place_translation_map.get(place)
        if translation_key:
            return get_string(translation_key)
        return place  # Fallback to English if translation not found
    
    def start_navigation(self, place: str, btn_name: str):
        self.ui.btn_home_navi.setEnabled(False)
        _set_navigation_buttons_enabled(self.ui, False)

        if place == self.current_place:
            if btn_name is None:
                print(constants.ERROR_BTN_NAME_NONE.format(place=place))
                return
            already_here_text = get_string(stringIds.NAV_ALREADY_HERE)
            self.ui.prompt_navi.setText(already_here_text)
            self.speaker.say(already_here_text)
            self.speaker.connect_finished(lambda: [
                SetStyleSheetForbtn(self.ui, btn_name, colors.COLOR_WHITE),
                self.ui.btn_home_navi.setEnabled(True),
                self.ui.btn_home_navi.setEnabled(True),
                self.ui.prompt_navi.setText(get_string(stringIds.NAV_WHERE_TO_GO))
            ])
            return

        self.location_manager.send_goal(place) 
        SetStyleSheetForbtn(self.ui, btn_name, colors.COLOR_GREEN)
        translated_place = self._get_translated_place(place)

        # Dọn kết nối cũ
        try:
            self.arrival_manager.subscriber_thread.arrival_update.disconnect()
        except TypeError:
            pass

        self.speaker.say(get_string(stringIds.NAV_LETS_MOVE, place=translated_place))
        self.speaker.connect_finished(lambda:[_set_navigation_buttons_enabled(self.ui, False),
                                              self.ui.btn_home_navi.setEnabled(False)])
        
        if self.current_place != place:
            self.stop_prompt = _animate_prompt(
                base_text=get_string(stringIds.NAV_HEADING_TO, place=translated_place),
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
                print(constants.ERROR_BTN_NAME_NONE.format(place=place))
                return

            translated_place = self._get_translated_place(place)
            
            self.speaker.say(get_string(stringIds.NAV_ARRIVED_AT, place=translated_place))
            self.speaker.connect_finished(lambda: [
                self.ui.btn_home_navi.setEnabled(True),
                _set_navigation_buttons_enabled(self.ui, True),
                self.ui.prompt_navi.setText(get_string(stringIds.NAV_ARRIVED_READY, place=translated_place)),
                SetStyleSheetForbtn(self.ui, btn_name, colors.COLOR_WHITE)
            ])


    def go_to_main_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)
        self.ui.prompt_navi.setText(get_string(stringIds.NAV_WHERE_TO_GO))

    def cleanup_thread(self, thread: QThread):
        if thread is not None:
            thread.quit()
            thread.wait()
            thread.deleteLater()
            thread = None
    
    def set_language_manager(self, lang_manager):
        self.lang_manager = lang_manager
    
    def _update_room_buttons(self):
        for place, btn_name in self.place_button_pairs:
            button = getattr(self.ui, btn_name, None)
            if button:
                translation_key = self.place_translation_map.get(place)
                if translation_key:
                    translated_place = get_string(translation_key)
                    button.setText(translated_place)
                else:
                    button.setText(place)
                
                try:
                    button.clicked.disconnect()
                except TypeError:
                    pass
                
                button.clicked.connect(lambda checked=False, p=place, b=btn_name: [
                    self.start_navigation(p, b),
                    SetStyleSheetForbtn(self.ui, b, "#69ff3d")
                ])
    
    def update_language(self):
        self.ui.prompt_navi.setText(get_string(stringIds.NAV_WHERE_TO_GO))
        self._update_room_buttons()