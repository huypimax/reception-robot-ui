from ui.main_ui import Ui_MainWindow
from pathplanning import LocationManager, ArrivalManager
from ui.widget_conf.dialog_utils import show_custom_dialog
from ui.widget_conf.ui_utils import SetStyleSheetForbtn, _animate_prompt
from language_manager import get_language_manager, get_string, update_widgets_auto
import utilities.string_ids as stringIds
import utilities.constants as constants
import utilities.colors as colors

class DeliPage:
    def __init__(self, main: Ui_MainWindow):
        self.ui = main
        self.lang_manager = get_language_manager()
        self.arrival_manager = ArrivalManager(self.ui)
        self.location_manager = LocationManager(self.ui, self.arrival_manager)
        self.location_manager.start_location_subscriber()
        self.is_waiting_deli = True

        self.ui.btn_home_deli.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_main))
        self.ui.start_deli_btn.clicked.connect(lambda: self.handle_deli_btn())

    def handle_deli_btn(self):
        if self.is_waiting_deli:
            self.handle_deli()
        else:
            self.handle_receive()
             
    def handle_deli(self):
        sender = self.ui.deli_sender.text()
        receiver = self.ui.deli_receiver.text()
        item = self.ui.deli_item.text()
        note = self.ui.deli_note.text()
        dest = self.ui.deli_combobox.currentText()

        if dest == constants.DEFAULT_DESTINATION_PLACEHOLDER:
            show_custom_dialog(constants.DIALOG_TITLE_DELIVERY_FAILED, constants.DIALOG_MSG_NO_DESTINATION, main_window=self.ui)
            return
        if sender == "":
            show_custom_dialog(constants.DIALOG_TITLE_DELIVERY_FAILED, constants.DIALOG_MSG_NO_SENDER, main_window=self.ui)
            return
        if receiver == "":
            show_custom_dialog(constants.DIALOG_TITLE_DELIVERY_FAILED, constants.DIALOG_MSG_NO_RECEIVER, main_window=self.ui)
            return
        if item == "":
            show_custom_dialog(constants.DIALOG_TITLE_DELIVERY_FAILED, constants.DIALOG_MSG_NO_ITEM, main_window=self.ui)
            return
        
        self.location_manager.send_goal(dest.strip())
        self.start_deli()

    def start_deli(self):
        self.is_waiting_deli = not self.is_waiting_deli
        self.form_enable_status(False)
        SetStyleSheetForbtn(self.ui, "start_deli_btn", colors.COLOR_RED, border_radius=colors.BORDER_RADIUS_DEFAULT, text_color=colors.COLOR_WHITE, hover_background=colors.COLOR_RED, hover_color=colors.COLOR_WHITE)
        self.stop_prompt = _animate_prompt(
            base_text=get_string(stringIds.DELI_DELIVERING_NOW),
            label_widget=self.ui.prompt_deli
        )
        self.arrival_manager.start_arrival_subscriber()
        self.arrival_manager.subscriber_thread.arrival_update.connect(
            lambda arrived: self.done_deli(arrived)
        )

    def done_deli(self, arrived):
        if arrived:
            if hasattr(self, "stop_prompt") and self.stop_prompt:
                self.stop_prompt()
                self.stop_prompt = None
            self.ui.prompt_deli.setText(get_string(stringIds.DELI_ITEM_ARRIVED))
            self.ui.start_deli_btn.setText(get_string(stringIds.DELI_RECEIVED))
            SetStyleSheetForbtn(self.ui, "start_deli_btn", colors.COLOR_DARK_BLUE, border_radius=colors.BORDER_RADIUS_DEFAULT, text_color=colors.COLOR_WHITE, hover_background=colors.COLOR_LIGHT_BLUE, hover_color=colors.COLOR_DARK_BLUE)
            self.ui.start_deli_btn.setEnabled(True)

    def handle_receive(self):
        self.form_enable_status(True)
        self.set_default()

    def form_enable_status(self, enable):
        self.ui.prompt_deli.setText(get_string(stringIds.DELI_GET_READY))
        self.ui.btn_home_deli.setEnabled(enable)
        self.ui.deli_sender.setEnabled(enable)
        self.ui.deli_receiver.setEnabled(enable)
        self.ui.deli_item.setEnabled(enable)
        self.ui.deli_note.setEnabled(enable)
        self.ui.deli_combobox.setEnabled(enable)
        self.ui.start_deli_btn.setEnabled(enable)
 
    def set_default(self):
        self.is_waiting_deli = not self.is_waiting_deli
        self.ui.deli_sender.setText("")
        self.ui.deli_receiver.setText("")
        self.ui.deli_item.setText("")
        self.ui.deli_note.setText("")
        self.ui.deli_combobox.setCurrentText(constants.DEFAULT_DESTINATION_PLACEHOLDER)
        self.ui.start_deli_btn.setText(get_string(stringIds.DELI_START_DELIVERY))
        SetStyleSheetForbtn(self.ui, "start_deli_btn", colors.COLOR_DARK_BLUE, border_radius=colors.BORDER_RADIUS_DEFAULT, text_color=colors.COLOR_WHITE, hover_background=colors.COLOR_LIGHT_BLUE, hover_color=colors.COLOR_DARK_BLUE)
    
    def set_language_manager(self, lang_manager):
        self.lang_manager = lang_manager
    
    def update_language(self):
        self.ui.prompt_deli.setText(get_string(stringIds.DELI_GET_READY))
        
        if hasattr(self.ui, 'label_9'):
            self.ui.label_9.setText(get_string(stringIds.DELI_FORM_TITLE))
        if hasattr(self.ui, 'label_12'):
            self.ui.label_12.setText(get_string(stringIds.DELI_DESTINATION))
        if hasattr(self.ui, 'label_11'):
            self.ui.label_11.setText(get_string(stringIds.DELI_ITEM_LABEL))
        if hasattr(self.ui, 'label_13'):
            self.ui.label_13.setText(get_string(stringIds.DELI_RECEIVER_LABEL))
        if hasattr(self.ui, 'label_10'):
            self.ui.label_10.setText(get_string(stringIds.DELI_SENDER_LABEL))
        if hasattr(self.ui, 'label_14'):
            self.ui.label_14.setText(get_string(stringIds.DELI_NOTE_LABEL))
        
        if hasattr(self.ui, 'deli_combobox'):
            placeholder = get_string(stringIds.DELI_CHOOSE_DESTINATION)
            self.ui.deli_combobox.setItemText(0, placeholder)
            # Nếu đang ở item 0 (placeholder), update current text
            if self.ui.deli_combobox.currentIndex() == 0:
                self.ui.deli_combobox.setCurrentText(placeholder)
        
        if hasattr(self.ui, 'start_deli_btn'):
            if self.is_waiting_deli:
                self.ui.start_deli_btn.setText(get_string(stringIds.DELI_START_DELIVERY))
            else:
                self.ui.start_deli_btn.setText(get_string(stringIds.DELI_RECEIVED))