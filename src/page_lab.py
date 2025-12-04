from ui.main_ui import Ui_MainWindow
from thread_speak import SpeakThread

class LabPage:
    device_info = {
        "btn_IFM_read": """This training kit demonstrates an industrial automation system using IO-Link communication and PROFINET connectivity integrated with a PLC.The setup includes an IO-Link Master (AL1102) connected to multiple IO-Link devices such as sensors (KT5112, O5C500, TW2000, IF6153, UGT524, RB3100) and I/O modules (AL2401 DI and AL2330 DO). 
                            Power is supplied through a 24V DC power module (DN4012) with a Y-splitter (EBC113) for distribution. The digital outputs control an Omron G2R1-SN relay, light indicators, and an RS775 DC motor, allowing the system to perform monitoring and actuation tasks. 
                            This kit provides a complete demonstration of sensor integration, signal processing, and control via industrial communication networks, making it ideal for training and automation experiments.""",
        
        "btn_step_read": """This training kit demonstrates a motion control system using Siemens PLC S7-1200 with PROFINET communication. The setup includes a Master PLC and a Slave PLC connected through an Ethernet hub, with an HMI for monitoring and control. 
                            The PLC sends control signals to a TB6600 stepper motor driver, which drives a stepper motor coupled to a lead screw shaft for linear motion. A signal encoder provides A, B, Z feedback signals for position monitoring, enabling precise closed-loop control and synchronization between the PLCs. 
                            This kit is ideal for studying PLC-based motion control, PROFINET communication, and encoder feedback integration in industrial automation.""",
        
        "btn_PLC_read": """A Programmable Logic Controller (PLC) is an industrial digital computer designed to control and automate machines, production lines, or processes. 
                            It continuously monitors input signals from sensors, processes them according to a user-defined program, and generates output signals to actuators such as motors, relays, and indicators. PLC systems are widely used because of their reliability, flexibility, real-time operation, and ease of programming.""",
        
        "btn_HMI_read": """A Human Machine Interface (HMI) is a device or software platform that allows operators to interact with machines, systems, or processes. It displays real-time data from the controller (such as a PLC) and enables users to monitor, control, and adjust system parameters through a graphical interface. 
                            HMIs can range from simple text displays to advanced touchscreens with animations, alarms, and data logging features. They play a key role in improving system visualization, operational efficiency, and troubleshooting in industrial automation."""
    }

    def __init__(self, main: Ui_MainWindow):
        self.ui = main

        self.ui.btn_IFM_2.clicked.connect(lambda: [self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_IFM)])
        self.ui.btn_step_2.clicked.connect(lambda: [self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_step)])
        self.ui.btn_PLC.clicked.connect(lambda: [self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_PLC)])
        self.ui.btn_HMI.clicked.connect(lambda: [self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_HMI)])

        self.ui.btn_home_lab_main.clicked.connect(lambda: [self.ui.stackedWidget.setCurrentWidget(self.ui.page_main), self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_main)])
        self.ui.btn_home_lab_IFM.clicked.connect(lambda: [self.ui.stackedWidget.setCurrentWidget(self.ui.page_main), self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_main)])
        self.ui.btn_home_lab_PLC.clicked.connect(lambda: [self.ui.stackedWidget.setCurrentWidget(self.ui.page_main), self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_IFM)])
        self.ui.btn_home_lab_step.clicked.connect(lambda: [self.ui.stackedWidget.setCurrentWidget(self.ui.page_main), self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_step)])
        self.ui.btn_home_lab_HMI.clicked.connect(lambda: [self.ui.stackedWidget.setCurrentWidget(self.ui.page_main), self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_PLC)])

        self.ui.btn_back_lab_IFM.clicked.connect(lambda: [self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_main)])
        self.ui.btn_back_lab_step.clicked.connect(lambda: [self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_main)])
        self.ui.btn_back_lab_PLC.clicked.connect(lambda: [self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_IFM)])
        self.ui.btn_back_lab_HMI.clicked.connect(lambda: [self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_step)])

        self.ui.btn_IFM_read.clicked.connect(lambda: [self.read_btn_handle("btn_IFM_read")])
        self.ui.btn_step_read.clicked.connect(lambda: [self.read_btn_handle("btn_step_read")])
        self.ui.btn_PLC_read.clicked.connect(lambda: [self.read_btn_handle("btn_PLC_read")])
        self.ui.btn_HMI_read.clicked.connect(lambda: [self.read_btn_handle("btn_HMI_read")])

    def read_btn_handle(self, btn: str):
        self.disable_all_buttons()
        btn_text = self.device_info[btn]
        self.speak_thread = SpeakThread(btn_text)
        self.speak_thread.finished.connect(lambda: [self.cleanup_thread(self.speak_thread), self.enable_all_buttons()])
        self.speak_thread.start()

    def disable_all_buttons(self):
        self.ui.btn_IFM_2.setEnabled(False)
        self.ui.btn_step_2.setEnabled(False)
        self.ui.btn_PLC.setEnabled(False)
        self.ui.btn_HMI.setEnabled(False)
        self.ui.btn_home_lab_main.setEnabled(False)
        self.ui.btn_home_lab_IFM.setEnabled(False)
        self.ui.btn_home_lab_PLC.setEnabled(False)
        self.ui.btn_home_lab_step.setEnabled(False)
        self.ui.btn_home_lab_HMI.setEnabled(False)
        self.ui.btn_back_lab_IFM.setEnabled(False)
        self.ui.btn_back_lab_step.setEnabled(False)
        self.ui.btn_back_lab_PLC.setEnabled(False)
        self.ui.btn_back_lab_HMI.setEnabled(False)
        self.ui.btn_IFM_read.setEnabled(False)
        self.ui.btn_step_read.setEnabled(False)
        self.ui.btn_HMI_read.setEnabled(False)
        self.ui.btn_PLC_read.setEnabled(False)

    def enable_all_buttons(self):
        self.ui.btn_IFM_2.setEnabled(True)
        self.ui.btn_step_2.setEnabled(True)
        self.ui.btn_PLC.setEnabled(True)
        self.ui.btn_HMI.setEnabled(True)
        self.ui.btn_home_lab_main.setEnabled(True)
        self.ui.btn_home_lab_IFM.setEnabled(True)
        self.ui.btn_home_lab_PLC.setEnabled(True)
        self.ui.btn_home_lab_step.setEnabled(True)
        self.ui.btn_home_lab_HMI.setEnabled(True)
        self.ui.btn_back_lab_IFM.setEnabled(True)
        self.ui.btn_back_lab_step.setEnabled(True)
        self.ui.btn_back_lab_PLC.setEnabled(True)
        self.ui.btn_back_lab_HMI.setEnabled(True)
        self.ui.btn_IFM_read.setEnabled(True)
        self.ui.btn_step_read.setEnabled(True)
        self.ui.btn_HMI_read.setEnabled(True)
        self.ui.btn_PLC_read.setEnabled(True)

    def cleanup_thread(self, thread: SpeakThread):
        if thread is not None:
            thread.quit()
            thread.wait()
            thread.deleteLater()
            thread = None
