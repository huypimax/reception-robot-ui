from PyQt6.QtCore import QThread, pyqtSignal
import asyncio
import datetime
import google.generativeai as genai


ASSISTANT_NAME = "AIko"
conversation_history = [
    {"role": "user", "parts": [{"text": "You are AIko, a friendly, concise receptionist assistant from Fablab HCMUT."}]},
    {"role": "model", "parts": [{"text": "Got it! I'm AIko, nice to meet you."}]},
]
last_reply = ""

class ResponseThread(QThread):
    finished = pyqtSignal(str)  # Signal to emit the response text
    def __init__(self, query, intial_context=None):
        super().__init__()
        self.query = query.lower()  # Normalize the query to lowercase
        self.api_key = "AIzaSyBXB9WorUWhgIVTZxqgSnZwC04HLgMTzis"  # ← thay bằng key thật
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")


    def run(self):
        global last_reply, conversation_history

        if any(kw in self.query for kw in ["stop", "bye", "thank you"]):
            reply = "You're welcome. Goodbye!"
        elif "time" in self.query:
            reply = f"It is {datetime.datetime.now().strftime('%I:%M %p')}."
        elif any(kw in self.query for kw in ["what day", "what date"]):
            reply = f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."
        elif any(kw in self.query for kw in ["repeat", "say it again"]):
            reply = last_reply or "I haven't said anything yet."
        else:
            faq_answer = self.check_faq(self.query)
            if faq_answer:
                reply = faq_answer
            else:
                # --- Câu hỏi chung: gửi qua Gemini ---
                reply = self.ask_gemini(self.query)

        last_reply = reply
        self.finished.emit(reply)



    def check_faq(self, query: str):
        self.query = query.lower()

        if any(kw in query for kw in [
            "ho chi minh university of technology", "bach khoa", "ho chi minh city university",
            "bach khoa university", "ho chi minh university", "ho chi minh city university of technology",
        ]):
            return ("Ho Chi Minh City University of Technology, also known as Bách Khoa, "
                    "is one of Vietnam’s top technical universities. It offers advanced training "
                    "in engineering, technology, and innovation, and is part of the Vietnam National University system.")
        
        elif any(kw in query for kw in [
            "ivs", "ivs company", "ivs joint stock company", "individual systems", "ibs company"]):
            return ("IVS Joint Stock Company is an IT enterprise founded in 2002, "
                    "specializing in software solutions, automation, and digital transformation for businesses. "
                    "With a team of hundreds of engineers, IVS has delivered numerous projects in manufacturing management, AI, and IoT across Vietnam and internationally.")

        elif any(kw in query for kw in [
            "fablab", "innovation lab", "robotics lab", 
            "fab lab", "the lab", "innovation laboratory", "fablab laboratory"
        ]):
            return "Fablab is an innovation lab at Ho Chi Minh University of Technology, supporting students in robotics, AI, and creative projects."

        elif any(kw in query for kw in [
            "how many people are there in the lab", "how many people work in the lab", "how many members in the lab"
        ]):
            return "Fablab currently has 23 members, including students from Electrical, Mechanical, and Computer Science departments." 

        elif any(kw in query for kw in [
            "who created you", "your creator", "who made you", "who built you", 
            "who developed you", "who designed you", "who creates you"
        ]):
            return "I was created by a group of students from Fablab laboratory, including members from Electrical and Mechanical departments."

        elif any(kw in query for kw in [
            "what's your name", "what is your name", "your name", "who are you"
        ]):
            return "My name is AIko, your friendly receptionist assistant."
        elif any(kw in query for kw in ["help", "what can you do", "what are your functions"]):
            return ("I can answer questions, tell the time, and guide you with basic information. Just ask me anything.")
        else:
            return None
        
    def ask_gemini(self, prompt):
        global conversation_history
        try:
            # Thêm câu hỏi mới của user vào history
            conversation_history.append({"role": "user", "parts": [{"text": prompt}]})
            
            # Gọi API với toàn bộ history
            response = self.model.generate_content(conversation_history)
            
            # Lấy text trả lời
            reply_text = response.text.strip()

            # Thêm phản hồi vào history để duy trì hội thoại
            conversation_history.append({"role": "model", "parts": [{"text": reply_text}]})
            
            return reply_text
        except Exception as e:
            print("Gemini error:", e)
            return "Sorry, I have trouble getting an answer."



