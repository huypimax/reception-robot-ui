from ui.main_ui import Ui_MainWindow

class LabPage:
    def __init__(self, main: Ui_MainWindow):
        self.ui = main
        self.setup_connections()
        self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_main)

    def setup_connections(self):
        self.ui.btn_lab.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_lab))
        self.ui.btn_IFM_2.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_IFM))
        self.ui.btn_step_2.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_step))
        self.ui.btn_PLC.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_PLC))
        self.ui.btn_HMI.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_HMI))

        self.ui.btn_home_lab_main.clicked.connect(self.go_home)
        self.ui.btn_home_lab_IFM.clicked.connect(self.go_home)
        self.ui.btn_home_lab_PLC.clicked.connect(self.go_home)
        self.ui.btn_home_lab_step.clicked.connect(self.go_home)
        self.ui.btn_home_lab_HMI.clicked.connect(self.go_home)

        self.ui.btn_back_lab_IFM.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_main))
        self.ui.btn_back_lab_step.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_main))
        self.ui.btn_back_lab_PLC.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_IFM))
        self.ui.btn_back_lab_HMI.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_step))

    def go_home(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)
