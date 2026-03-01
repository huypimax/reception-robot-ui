from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QTimer

def _animate_prompt(base_text: str, label_widget, callback_after=None):
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

    def stop():
        timer.stop()
        if callback_after:
            callback_after()

    return stop

def shadow(objects, blur=20, x_offset=4, y_offset=4, color=QColor(0, 0, 0, 150)):
    """Áp dụng hiệu ứng bóng cho đối tượng"""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setXOffset(x_offset)
    shadow.setYOffset(y_offset)
    shadow.setColor(color)
    objects.setGraphicsEffect(shadow)

def SetStyleSheetForbtn(ui, btn, background_color, border_radius="30px", text_color="black", hover_background="#ffffff", hover_color="black"):
    """Set background cho nút"""
    button = getattr(ui, btn)
    button.setStyleSheet(f"""
        QPushButton#{btn} {{
            border-radius: {border_radius};
            border-color: white;
            background-color: {background_color};
            color: {text_color};
            text-align: center;
            font-family: Inter, sans-serif;
        }}

        QPushButton#{btn}:hover {{
            background-color: {hover_background};
            color: {hover_color};
        }}

        QPushButton#{btn}:pressed {{
            padding-left: 5px;
            padding-top: 5px;
        }}
    """)


def _set_navigation_buttons_enabled(ui, enabled: bool):
    for name in ["btn_room_1", 
                 "btn_room_2", 
                 "btn_room_3", 
                 "btn_room_4", 
                 "btn_room_5", 
                 "btn_room_6", 
                 "btn_room_7", 
                 "btn_room_8", 
                 "btn_room_9"]:
        getattr(ui, name).setEnabled(enabled)

def set_color_btn_room(ui, color):
    SetStyleSheetForbtn(ui, "btn_room_1", color)
    SetStyleSheetForbtn(ui, "btn_room_2", color)
    SetStyleSheetForbtn(ui, "btn_room_3", color)
    SetStyleSheetForbtn(ui, "btn_room_4", color)
    SetStyleSheetForbtn(ui, "btn_room_5", color)
    SetStyleSheetForbtn(ui, "btn_room_6", color)
    SetStyleSheetForbtn(ui, "btn_room_7", color)
    SetStyleSheetForbtn(ui, "btn_room_8", color)
    SetStyleSheetForbtn(ui, "btn_room_9", color)