from ui.main_ui import Ui_MainWindow

class DeliPage:
    def __init__(self, main: Ui_MainWindow):
        self.ui = main
        self.ui.btn_deli.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_deli))
        self.ui.btn_home_deli.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_main))
