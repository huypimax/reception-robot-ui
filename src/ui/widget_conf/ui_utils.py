from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QTimer

def _animate_prompt(base_text: str, label_widget, duration_ms, callback_after=None):
    """ Hiệu ứng động "..." sau base_text """
    dots = [".", "...", "......"]
    index = 0
    timer = QTimer()

    def update():
        nonlocal index
        label_widget.setText(f"{base_text}{dots[index]}")
        index = (index + 1) % len(dots)

    timer.timeout.connect(update)
    timer.start(500)  # mỗi 500ms update chấm

    # Sau duration_ms thì stop hiệu ứng và gọi callback nếu có
    QTimer.singleShot(duration_ms, lambda: (timer.stop(), callback_after() if callback_after else None))


def shadow(objects, blur=20, x_offset=4, y_offset=4, color=QColor(0, 0, 0, 150)):
    """Áp dụng hiệu ứng bóng cho đối tượng"""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setXOffset(x_offset)
    shadow.setYOffset(y_offset)
    shadow.setColor(color)
    objects.setGraphicsEffect(shadow)

def SetStyleSheetForbtn(ui, btn, background_color, text_color="black", hover_background="#ffffff"):
    """Set background cho nút"""
    button = getattr(ui, btn)
    button.setStyleSheet(f"""
        QPushButton#{btn} {{
            border-radius: 30px;
            border-color: white;
            background-color: {background_color};
            color: {text_color};
            text-align: center;
            font-family: Inter, sans-serif;
        }}

        QPushButton#{btn}:hover {{
            background-color: {hover_background};
        }}

        QPushButton#{btn}:pressed {{
            padding-left: 5px;
            padding-top: 5px;
        }}
    """)

