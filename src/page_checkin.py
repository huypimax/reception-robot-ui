from ui.main_ui import Ui_MainWindow

class CheckinPage:
    def __init__(self, main: Ui_MainWindow):
        self.ui = main
        self.ui.btn_check_in.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_checkin))
        self.ui.btn_home_checkin.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_main))
