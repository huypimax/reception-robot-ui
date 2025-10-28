import threading, requests, time
from PyQt6.QtCore import QUrl, QTimer, QLoggingCategory
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QWidget, QVBoxLayout

# Tat log từ Qt WebEngine
QLoggingCategory.setFilterRules("qt.webenginecontext=false")

class WebTab(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.url_str = "https://hcmut.edu.vn/virtual-tour/"
        self.url = QUrl(self.url_str)

        self.browser = QWebEngineView()
        self.browser.setUrl(self.url)

        layout = self.ui.web_layout.layout()
        if layout is None:
            layout = QVBoxLayout(self.ui.web_layout)
            self.ui.web_layout.setLayout(layout)
        layout.addWidget(self.browser)

        # Trạng thái kết nối cũ
        self.connected = True

        # Khởi động luồng kiểm tra kết nối camera
        self.check_thread = threading.Thread(target=self.check_connection_loop, daemon=True)
        self.check_thread.start()

    def check_connection_loop(self):
        while True:
            try:
                res = requests.get(self.url_str, timeout=2)
                if res.status_code == 200:
                    if not self.connected:
                        self.connected = True
                        QTimer.singleShot(0, self.restore_browser)
                else:
                    raise Exception("bad status")
            except:
                if self.connected:
                    self.connected = False
            import time
            time.sleep(5)

    def restore_browser(self):
        self.browser.setUrl(self.url)
