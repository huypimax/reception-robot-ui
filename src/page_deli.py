from ui.main_ui import Ui_MainWindow
from pathplanning import LocationManager, ArrivalManager
from ui.widget_conf.dialog_utils import show_custom_dialog
from ui.widget_conf.ui_utils import SetStyleSheetForbtn, _animate_prompt

class DeliPage:
    def __init__(self, main: Ui_MainWindow):
        self.ui = main
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

        if dest == " Choose a destination":
            show_custom_dialog("Delivery Failed", "Oops! You haven’t chosen a destination yet", main_window=self.ui)
            return
        if sender == "":
            show_custom_dialog("Delivery Failed", "Enter the sender, please", main_window=self.ui)
            return
        if receiver == "":
            show_custom_dialog("Delivery Failed", "Enter the receiver, please", main_window=self.ui)
            return
        if item == "":
            show_custom_dialog("Delivery Failed", "Enter the item, please", main_window=self.ui)
            return
        
        self.location_manager.send_goal(dest.strip())
        self.start_deli()

    def start_deli(self):
        self.is_waiting_deli = not self.is_waiting_deli
        self.form_enable_status(False)
        SetStyleSheetForbtn(self.ui, "start_deli_btn", "#ac0000", border_radius="10px", text_color="white", hover_background="#ac0000", hover_color="white")
        self.stop_prompt = _animate_prompt(
            base_text=f"I’m delivering your item now",
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
            self.ui.prompt_deli.setText("Your item is here! Please collect it and press ‘Received’ on the bottom-left of the form")
            self.ui.start_deli_btn.setText("Received")
            SetStyleSheetForbtn(self.ui, "start_deli_btn", "#00294D", border_radius="10px", text_color="white", hover_background="#D8E5FE", hover_color="#00294D")
            self.ui.start_deli_btn.setEnabled(True)

    def handle_receive(self):
        self.form_enable_status(True)
        self.set_default()

    def form_enable_status(self, enable):
        self.ui.prompt_deli.setText("Let’s get your delivery ready! Please fill in the form and tap 'Start delivery' when done.")
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
        self.ui.deli_combobox.setCurrentText(" Choose a destination")
        self.ui.start_deli_btn.setText("Start delivery")
        SetStyleSheetForbtn(self.ui, "start_deli_btn", "#00294D", border_radius="10px", text_color="white", hover_background="#D8E5FE", hover_color="#00294D")