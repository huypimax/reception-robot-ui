# ui/font_configurator.py

from ui.resources.fonts import set_bold, set_regular

def apply_custom_fonts(ui):
    #main 
    set_bold(ui.prompt_main)
    set_bold(ui.label_2)
    set_bold(ui.label_5)
    set_bold(ui.label_21)

    #qna
    set_bold(ui.prompt_qna)
    
    #navi 
    set_bold(ui.prompt_navi)
    set_bold(ui.btn_room_a)
    set_bold(ui.btn_room_b)
    set_bold(ui.btn_room_c)
    set_bold(ui.btn_room_d)