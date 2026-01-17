import sys
import os
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QObject, pyqtSlot, QUrl

current_dir = os.path.dirname(os.path.abspath(__file__))
qml_file_path = os.path.join(current_dir, "view.qml")

# Class cầu nối Python - QML
class BackendBridge(QObject):
    @pyqtSlot(str)
    def receive_command(self, command):
        print(f"Python nhận lệnh: {command}")

app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()

backend = BackendBridge()
engine.rootContext().setContextProperty("backend", backend)


if not os.path.exists(qml_file_path):
    print(f"File not found: {qml_file_path}")
    sys.exit(-1)

engine.load(QUrl.fromLocalFile(qml_file_path))

if not engine.rootObjects():
    sys.exit(-1)

sys.exit(app.exec())