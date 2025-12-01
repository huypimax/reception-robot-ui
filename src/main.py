# ==== FIX WHISPER + PYTORCH + PYQT6 TRÊN WINDOWS INTEL UHD ====
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"          # vẫn cần
os.environ["OMP_NUM_THREADS"] = "1"

# Dòng thần thánh cứu cả Whisper và faster-whisper
os.environ["MKL_THREADING_LAYER"] = "GNU"            # <<< quan trọng nhất
os.environ["KMP_AFFINITY"] = "disabled"              # tắt Intel OpenMP hoàn toàn
os.environ["CUDA_VISIBLE_DEVICES"] = ""   # phòng trường hợp nó tìm GPU
# =============================================================
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import QThread
from ui.main_ui import Ui_MainWindow
from pathplanning import LocationManager
from ui.fonts_conf.font_configurator import apply_custom_fonts
from ui.widget_conf.apply_utils import apply_shadow
from ui.widget_conf.ui_utils import SetStyleSheetForbtn, _animate_prompt, _set_navigation_buttons_enabled, set_color_btn_room

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

        # Gắn các page
        self.qna_page = QnaPage(self, initial_context)
        self.btn_qna.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_qna), self.prompt_qna.setText("Tap the microphone to ask anything."),
                                              self.qna_page.start_welcome(), self.btn_home_qna.setEnabled(False), self.btn_micro.setEnabled(False)])

        self.navi_page = NaviPage(self)
        self.btn_navi.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_navi), 
                                               self.navi_page.handle_btn_navi(), 
                                               self.btn_home_navi.setEnabled(False), 
                                               _set_navigation_buttons_enabled(self, False), 
                                               set_color_btn_room(self, "#ffffff"), 
                                               self.prompt_navi.setText("Where do you want to go?"),
                                               ])

        self.lab_page = LabPage(self)
        self.btn_lab.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_lab), self.stackedWidget_2.setCurrentWidget(self.page_lab_main)])

        self.deli_page = DeliPage(self)
        self.btn_deli.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_deli)])

        self.checkin_page = CheckinPage(self)
        self.btn_check_in.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_checkin)])


    def go_to_main_page(self):
        self.stackedWidget.setCurrentWidget(self.page_main)

    def cleanup_thread(self, thread: QThread):
        if thread is not None:
            thread.quit()
            thread.wait()
            thread.deleteLater()
            thread = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec())
