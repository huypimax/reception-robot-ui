import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread
from ui.main_ui import Ui_MainWindow
from pathplanning import LocationManager
from ui.fonts_conf.font_configurator import apply_custom_fonts
from ui.widget_conf.apply_utils import apply_shadow
from ui.widget_conf.ui_utils import SetStyleSheetForbtn, _animate_prompt, _set_navigation_buttons_enabled, set_color_btn_room
from language_manager import get_language_manager, get_string, update_widgets_auto
import utilities.string_ids as stringIds
import utilities.constants as constants
import utilities.colors as colors

from page_qna import QnaPage
from page_navi import NaviPage
from page_lab import LabPage
from page_deli import DeliPage
from page_checkin import CheckinPage

def get_initial_context():
    from language_manager import get_language_manager
    lang_manager = get_language_manager()
    if lang_manager.get_current_language() == 'vi':
        return constants.INITIAL_CONTEXT_VI
    return constants.INITIAL_CONTEXT_EN

initial_context = None


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        apply_custom_fonts(self)
        apply_shadow(self)
        self.stackedWidget.setCurrentWidget(self.page_main)
        self.lang_manager = get_language_manager()
        current_initial_context = get_initial_context()
        self._create_language_button()

        # Gắn các page
        self.qna_page = QnaPage(self, current_initial_context)
        self.btn_qna.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_qna), 
                                              self.prompt_qna.setText(get_string(stringIds.QNA_TAP_MICROPHONE)),
                                              self.qna_page.start_welcome(), 
                                              self.btn_home_qna.setEnabled(False), 
                                              self.btn_micro.setEnabled(False)])

        self.navi_page = NaviPage(self)
        self.navi_page.set_language_manager(self.lang_manager)
        self.btn_navi.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_navi), 
                                               self.navi_page.handle_btn_navi(), 
                                               self.btn_home_navi.setEnabled(False), 
                                               _set_navigation_buttons_enabled(self, False), 
                                               set_color_btn_room(self, "#ffffff"), 
                                               self.prompt_navi.setText(get_string(stringIds.NAV_WHERE_TO_GO)),
                                               ])

        self.lab_page = LabPage(self)
        self.lab_page.set_language_manager(self.lang_manager)
        self.btn_lab.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_lab), 
                                              self.stackedWidget_2.setCurrentWidget(self.page_lab_main)])

        self.deli_page = DeliPage(self)
        self.deli_page.set_language_manager(self.lang_manager)
        self.btn_deli.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_deli)])

        self.checkin_page = CheckinPage(self)
        self.checkin_page.set_language_manager(self.lang_manager)
        # self.btn_check_in.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_checkin)])
        self.update_ui_language()

        if hasattr(self, 'qna_page'):
            self.qna_page.update_language()
        if hasattr(self, 'navi_page'):
            self.navi_page.update_language()
        if hasattr(self, 'lab_page'):
            self.lab_page.update_language()
        if hasattr(self, 'deli_page'):
            self.deli_page.update_language()
    
    def _create_language_button(self):
        self.btn_language = QPushButton(parent=self.page_main)
        self.btn_language.setMinimumSize(*constants.BTN_LANGUAGE_MIN_SIZE)
        self.btn_language.setMaximumSize(*constants.BTN_LANGUAGE_MAX_SIZE)
        self.btn_language.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.COLOR_WHITE};
                color: {colors.COLOR_BLUE_TEXT};
                border-radius: 10px;
                font-family: "{constants.FONT_FAMILY_ROBOTO}";
                font-size: {constants.FONT_SIZE_BUTTON}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors.COLOR_HOVER_BG};
            }}
        """)
        self.btn_language.clicked.connect(self.switch_language)
        
        main_widget = self.page_main.findChild(QtWidgets.QWidget, constants.WIDGET_MAIN_CONTAINER)
        if main_widget:
            layout = main_widget.layout()
            if layout:
                layout.insertWidget(0, self.btn_language)
        
        self.update_language_button_text()
    
    def update_language_button_text(self):
        self.btn_language.setText(self.lang_manager.get_language_name())

    def switch_language(self):
        self.lang_manager.toggle_language()
        self.update_language_button_text()
        self.update_ui_language()
        
        # Update tất cả các pages khác
        if hasattr(self, 'qna_page'):
            self.qna_page.update_language()
        if hasattr(self, 'navi_page'):
            self.navi_page.update_language()
        if hasattr(self, 'lab_page'):
            self.lab_page.update_language()
        if hasattr(self, 'deli_page'):
            self.deli_page.update_language()
        if hasattr(self, 'checkin_page'):
            if hasattr(self.checkin_page, 'update_language'):
                self.checkin_page.update_language()
    
    def update_ui_language(self):
        self.prompt_main.setText(get_string(stringIds.MAIN_TITLE))
        self.label_22.setText(get_string(stringIds.MAIN_LAB))
        self.label_2.setText(get_string(stringIds.MAIN_QNA))
        self.label_5.setText(get_string(stringIds.MAIN_NAVIGATION))
        self.label_23.setText(get_string(stringIds.MAIN_DELIVERY))


    def go_to_main_page(self):
        self.stackedWidget.setCurrentWidget(self.page_main)

    def cleanup_thread(self, thread: QThread):
        if thread is not None:
            thread.quit()
            thread.wait()
            thread.deleteLater()
            thread = None
    
    def retranslateUi(self, MainWindow):
        self.update_ui_language()
        
        if hasattr(self, 'qna_page'):
            self.qna_page.update_language()
        if hasattr(self, 'navi_page'):
            self.navi_page.update_language()
        if hasattr(self, 'lab_page'):
            self.lab_page.update_language()
        if hasattr(self, 'deli_page'):
            self.deli_page.update_language()
        if hasattr(self, 'btn_language'):
            self.update_language_button_text()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec())
