from ui.main_ui import Ui_MainWindow
# from thread_speak import SpeakThread
from thread_speak import SpeakManager
from language_manager import get_language_manager, get_string
import utilities.string_ids as stringIds
class LabPage:
    def __init__(self, main: Ui_MainWindow):
        self.ui = main
        self.speaker = SpeakManager()
        self.speaker.connect_finished(self.on_speak_finished)
        self.lang_manager = get_language_manager()

        self.ui.btn_IFM_2.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_IFM))
        self.ui.btn_step_2.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_step))
        self.ui.btn_PLC.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_PLC))
        self.ui.btn_HMI.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_lab_HMI))

        self.ui.btn_home_lab_main.clicked.connect(lambda: self.home_with_stop(self.ui.page_main, self.ui.page_lab_main))
        self.ui.btn_home_lab_IFM.clicked.connect(lambda: self.home_with_stop(self.ui.page_main, self.ui.page_lab_main))
        self.ui.btn_home_lab_PLC.clicked.connect(lambda: self.home_with_stop(self.ui.page_main, self.ui.page_lab_IFM))
        self.ui.btn_home_lab_step.clicked.connect(lambda: self.home_with_stop(self.ui.page_main, self.ui.page_lab_step))
        self.ui.btn_home_lab_HMI.clicked.connect(lambda: self.home_with_stop(self.ui.page_main, self.ui.page_lab_PLC))

        self.ui.btn_back_lab_IFM.clicked.connect(lambda: self.back_with_stop(self.ui.page_lab_main))
        self.ui.btn_back_lab_step.clicked.connect(lambda: self.back_with_stop(self.ui.page_lab_main))
        self.ui.btn_back_lab_PLC.clicked.connect(lambda: self.back_with_stop(self.ui.page_lab_IFM))
        self.ui.btn_back_lab_HMI.clicked.connect(lambda: self.back_with_stop(self.ui.page_lab_step))

        self.ui.btn_IFM_read.clicked.connect(lambda: self.on_read_clicked("btn_IFM_read", self.ui.btn_IFM_read))
        self.ui.btn_step_read.clicked.connect(lambda: self.on_read_clicked("btn_step_read", self.ui.btn_step_read))
        self.ui.btn_PLC_read.clicked.connect(lambda: self.on_read_clicked("btn_PLC_read", self.ui.btn_PLC_read))
        self.ui.btn_HMI_read.clicked.connect(lambda: self.on_read_clicked("btn_HMI_read", self.ui.btn_HMI_read))

    def read_btn_handle(self, btn: str):
        btn_text = self.device_info[btn]
        self.speaker.say(btn_text)

    def on_speak_finished(self, _text):
        self.enable_read_buttons()

    def on_read_clicked(self, key, button):
        button.setEnabled(False)
        self.read_btn_handle(key)

    def enable_read_buttons(self):
        self.ui.btn_IFM_read.setEnabled(True)
        self.ui.btn_step_read.setEnabled(True)
        self.ui.btn_PLC_read.setEnabled(True)
        self.ui.btn_HMI_read.setEnabled(True)

    def back_with_stop(self, widget):
        self.speaker.stop()
        self.enable_read_buttons()
        self.ui.stackedWidget_2.setCurrentWidget(widget)

    def home_with_stop(self, widget1, widget2):
        self.speaker.stop()
        self.enable_read_buttons()
        self.ui.stackedWidget.setCurrentWidget(widget1)
        self.ui.stackedWidget_2.setCurrentWidget(widget2)
    
    def set_language_manager(self, lang_manager):
        self.lang_manager = lang_manager
    
    def update_language(self):
        self.device_info = {
            "btn_IFM_read": get_string(stringIds.LAB_DEVICE_IFM),
            "btn_step_read": get_string(stringIds.LAB_DEVICE_STEP),
            "btn_PLC_read": get_string(stringIds.LAB_DEVICE_PLC),
            "btn_HMI_read": get_string(stringIds.LAB_DEVICE_HMI)
        }
        
        if hasattr(self.ui, 'prompt_lab'):
            self.ui.prompt_lab.setText(get_string(stringIds.LAB_PROMPT))
        
        if hasattr(self.ui, 'label_24'):
            self.ui.label_24.setText(get_string(stringIds.LAB_SYSTEM_DIAGRAM))
        if hasattr(self.ui, 'label_25'):
            self.ui.label_25.setText(get_string(stringIds.LAB_SYSTEM_DIAGRAM))
        
        if hasattr(self.ui, 'label_15'):
            self.ui.label_15.setText(get_string(stringIds.LAB_ABOUT_IFM))
        if hasattr(self.ui, 'label_34'):
            self.ui.label_34.setText(get_string(stringIds.LAB_ABOUT_PLC))
        if hasattr(self.ui, 'label_27'):
            self.ui.label_27.setText(get_string(stringIds.LAB_ABOUT_STEP))
        if hasattr(self.ui, 'label_40'):
            self.ui.label_40.setText(get_string(stringIds.LAB_ABOUT_HMI))
        
        if hasattr(self.ui, 'btn_IFM_read'):
            self.ui.btn_IFM_read.setText(get_string(stringIds.LAB_READ_ALOUD))
        if hasattr(self.ui, 'btn_PLC_read'):
            self.ui.btn_PLC_read.setText(get_string(stringIds.LAB_READ_ALOUD))
        if hasattr(self.ui, 'btn_step_read'):
            self.ui.btn_step_read.setText(get_string(stringIds.LAB_READ_ALOUD))
        if hasattr(self.ui, 'btn_HMI_read'):
            self.ui.btn_HMI_read.setText(get_string(stringIds.LAB_READ_ALOUD))
        
        ifm_full_text = self.device_info["btn_IFM_read"]
        if hasattr(self.ui, 'label_19'):
            # First sentence/paragraph of IFM description
            sentences = ifm_full_text.split('. ')
            if len(sentences) > 0:
                self.ui.label_19.setText(sentences[0] + ('.' if not sentences[0].endswith('.') else ''))
        if hasattr(self.ui, 'label_17'):
            # Second sentence/paragraph
            sentences = ifm_full_text.split('. ')
            if len(sentences) > 1:
                self.ui.label_17.setText(sentences[1] + ('.' if not sentences[1].endswith('.') else ''))
        if hasattr(self.ui, 'label_18'):
            # Third sentence/paragraph
            sentences = ifm_full_text.split('. ')
            if len(sentences) > 2:
                self.ui.label_18.setText(sentences[2] + ('.' if not sentences[2].endswith('.') else ''))
        if hasattr(self.ui, 'label_20'):
            # Last sentence/paragraph
            sentences = ifm_full_text.split('. ')
            if len(sentences) > 3:
                self.ui.label_20.setText('. '.join(sentences[3:]))
        
        plc_full_text = self.device_info["btn_PLC_read"]
        if hasattr(self.ui, 'label_35'):
            sentences = plc_full_text.split('. ')
            if len(sentences) > 0:
                self.ui.label_35.setText(sentences[0] + ('.' if not sentences[0].endswith('.') else ''))
        if hasattr(self.ui, 'label_36'):
            sentences = plc_full_text.split('. ')
            if len(sentences) > 1:
                self.ui.label_36.setText(sentences[1] + ('.' if not sentences[1].endswith('.') else ''))
        if hasattr(self.ui, 'label_37'):
            sentences = plc_full_text.split('. ')
            if len(sentences) > 2:
                self.ui.label_37.setText('. '.join(sentences[2:]))
        
        step_full_text = self.device_info["btn_step_read"]
        if hasattr(self.ui, 'label_28'):
            sentences = step_full_text.split('. ')
            if len(sentences) > 0:
                self.ui.label_28.setText(sentences[0] + ('.' if not sentences[0].endswith('.') else ''))
        if hasattr(self.ui, 'label_29'):
            sentences = step_full_text.split('. ')
            if len(sentences) > 1:
                self.ui.label_29.setText(sentences[1] + ('.' if not sentences[1].endswith('.') else ''))
        if hasattr(self.ui, 'label_30'):
            sentences = step_full_text.split('. ')
            if len(sentences) > 2:
                self.ui.label_30.setText(sentences[2] + ('.' if not sentences[2].endswith('.') else ''))
        if hasattr(self.ui, 'label_31'):
            sentences = step_full_text.split('. ')
            if len(sentences) > 3:
                self.ui.label_31.setText('. '.join(sentences[3:]))
        
        hmi_full_text = self.device_info["btn_HMI_read"]
        if hasattr(self.ui, 'label_41'):
            sentences = hmi_full_text.split('. ')
            if len(sentences) > 0:
                self.ui.label_41.setText(sentences[0] + ('.' if not sentences[0].endswith('.') else ''))
        if hasattr(self.ui, 'label_42'):
            sentences = hmi_full_text.split('. ')
            if len(sentences) > 1:
                self.ui.label_42.setText(sentences[1] + ('.' if not sentences[1].endswith('.') else ''))
        if hasattr(self.ui, 'label_43'):
            sentences = hmi_full_text.split('. ')
            if len(sentences) > 2:
                self.ui.label_43.setText(sentences[2] + ('.' if not sentences[2].endswith('.') else ''))
        if hasattr(self.ui, 'label_45'):
            sentences = hmi_full_text.split('. ')
            if len(sentences) > 3:
                self.ui.label_45.setText('. '.join(sentences[3:]))