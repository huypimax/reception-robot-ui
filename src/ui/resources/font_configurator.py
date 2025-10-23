# ui/font_configurator.py

from ui.resources.fonts import set_bold, set_regular

def apply_custom_fonts(ui):
    #main 
    set_bold(ui.prompt_main)
    set_bold(ui.label_2)
    set_bold(ui.label_5)
    set_bold(ui.label_21)
    set_bold(ui.label_22)
    set_bold(ui.label_23)

    #qna
    set_bold(ui.prompt_qna)
    
    #navi 
    set_bold(ui.prompt_navi)
    set_bold(ui.btn_room_a)
    set_bold(ui.btn_room_b)
    set_bold(ui.btn_room_c)
    set_bold(ui.btn_room_d)

    #deli
    set_bold(ui.label_9)
    set_bold(ui.label_10)
    set_bold(ui.label_11)
    set_bold(ui.label_12)
    set_bold(ui.label_13)
    set_bold(ui.label_14)

    #chekin
    set_bold(ui.prompt_checkin)
    