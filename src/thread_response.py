"""
ResponseThread sử dụng LangGraph workflow
"""
from PyQt6.QtCore import QThread, pyqtSignal
import os
import json
from ai.response_graph import ResponseGraph


import utilities.constants as constants
conversation_history = [
    {"role": "user", "parts": [{"text": "You are AIko, a friendly, concise receptionist assistant from Fablab HCMUT."}]},
    {"role": "model", "parts": [{"text": "Got it! I'm AIko, nice to meet you."}]},
]


class ResponseThread(QThread):
    """
    Thread xử lý response sử dụng LangGraph workflow
    """
    finished = pyqtSignal(str)  # Signal to emit the response text
    
    def __init__(self, query, response_graph: ResponseGraph, lang: str = "vi"):
        """
        Args:
            query: Câu hỏi từ user
            response_graph: ResponseGraph instance đã được khởi tạo
            lang: Ngôn ngữ (mặc định: "vi" - tiếng Việt)
        """
        super().__init__()
        self.query = query.lower()
        self.response_graph = response_graph
        self.lang = lang

    def run(self):
        """Chạy LangGraph workflow để xử lý query"""
        try:
            # Sử dụng LangGraph để xử lý query
            reply = self.response_graph.invoke(self.query, initial_messages=[])
            
            # Phát tín hiệu hoàn thành với reply
            self.finished.emit(reply)

        except Exception as e:
            print(f"Unexpected error in ResponseThread.run(): {e}")
            reply = "Đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau."
            self.finished.emit(reply)


# Export tools để backward compatibility (nếu có code khác đang dùng)
from ai.response_graph import search_web, get_weather, ALL_TOOLS
    

