import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer
from ui.main_ui import Ui_MainWindow
from ui.fonts_conf.font_configurator import apply_custom_fonts
from ui.widget_conf.apply_utils import apply_shadow

from page_qna import QnaPage
from page_navi import NaviPage
from page_lab import LabPage
from page_deli import DeliPage
from page_checkin import CheckinPage


ASSISTANT_NAME = "AIko"
initial_context = [
    {"role": "user", "parts": [{"text": "You are AIko, a helpful and concise virtual assistant created by Fablab."}]},
    {"role": "model", "parts": [{"text": "Got it. I'm AIko, your assistant from Fablab."}]},
    {"role": "user", "parts": [{"text": "When replying, use 1–2 sentences, under 35 words."}]},
    {"role": "model", "parts": [{"text": "Understood. I'll keep it concise and friendly."}]},
]

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        apply_custom_fonts(self)
        apply_shadow(self)
        self.stackedWidget.setCurrentWidget(self.page_main)
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(40000)  
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.go_to_main_page)

        # Gắn các page
        self.qna_page = QnaPage(self, initial_context)
        self.btn_qna.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_qna)])

        self.navi_page = NaviPage(self, self.inactivity_timer)
        self.btn_navi.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_navi), self.navi_page.handle_btn_navi()])

        self.lab_page = LabPage(self)
        self.btn_lab.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_lab_main)])

        self.deli_page = DeliPage(self)
        self.btn_deli.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_deli)])

        self.checkin_page = CheckinPage(self)
        self.btn_check_in.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_checkin)])

    def go_to_main_page(self):
        self.stackedWidget.setCurrentWidget(self.page_main)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec())
