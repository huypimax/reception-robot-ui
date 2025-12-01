from PyQt6.QtCore import QThread, pyqtSignal
import asyncio
import datetime
from google.genai import types
import google.genai as genai
import json, os, requests


ASSISTANT_NAME = "AIko"
conversation_history = [
    {"role": "user", "parts": [{"text": "You are AIko, a friendly, concise receptionist assistant from Fablab HCMUT."}]},
    {"role": "model", "parts": [{"text": "Got it! I'm AIko, nice to meet you."}]},
]
last_reply = ""

class ResponseThread(QThread):
    finished = pyqtSignal(str)  # Signal to emit the response text
    def __init__(self, query, chat_session, initial_context=None,lang: str = "en"):
        super().__init__()
        self.query = query.lower()
        self.chat_session = chat_session 
        self.initial_context = initial_context
        self.lang = lang

    def run(self):
        global last_reply, conversation_history

        try:
            # ==== Các câu trả lời offline ====
            if any(kw in self.query for kw in ["stop", "bye", "thank you"]):
                reply = "You're welcome. Goodbye!"

            elif "time" in self.query:
                reply = f"It is {datetime.datetime.now().strftime('%I:%M %p')}."

            elif any(kw in self.query for kw in ["what day", "what date"]):
                reply = f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."

            elif any(kw in self.query for kw in ["repeat", "say it again"]):
                reply = last_reply or "I haven't said anything yet."

            else:
                # ==== FAQ ====
                faq_answer = self.check_faq(self.query)
                if faq_answer:
                    reply = faq_answer
                else:
                    # ==== Gửi Gemini dạng synchronous ====
                    try:
                        response = self.chat_session.send_message(self.query)
                        while response.function_calls:
                            # Nếu Gemini yêu cầu gọi hàm:
                            function_calls = response.function_calls
                            # Danh sách kết quả thực thi các hàm
                            tool_results = []
                            
                            for call in function_calls:
                                # Lấy tên hàm và các đối số
                                function_name = call.name
                                function_args = dict(call.args)
                                result = None

                                # Tìm hàm tương ứng và thực thi
                                if function_name == "search_web":
                                    print(f"DEBUG: Gọi hàm search_web({function_args.get('query')})")
                                    if "query" in function_args:
                                        result = search_web(function_args["query"])
                                        tool_results.append(types.Part.from_function_response(
                                            name=function_name,
                                            response={'result': result}
                                        ))
                                    else:
                                        print("DEBUG: Thiếu tham số 'query' cho search_web")
                                    
                                elif function_name == "get_weather":
                                    print(f"DEBUG: Gọi hàm get_weather({function_args.get('city')})")
                                    
                                    # Kiểm tra tham số 'city'
                                    if "city" in function_args:
                                        result = get_weather(function_args["city"])
                                        tool_results.append(types.Part.from_function_response(
                                            name=function_name,
                                            response={'result': result}
                                        ))
                                    else:
                                        print("DEBUG: Thiếu tham số 'city' cho get_weather")
                            
                            # Gửi kết quả thực thi hàm trở lại Gemini
                            response = self.chat_session.send_message(self.query, tool_results)
                        
                        reply = response.text.strip()
                    except Exception as e:
                        print("Gemini error:", e)
                        reply = "Sorry, I have trouble getting an answer."

            # Lưu câu trả lời cuối cùng và phát tín hiệu hoàn thành
            last_reply = reply
            self.finished.emit(reply)

        except Exception as e:
            print("Unexpected error in run:", e)
            reply = "An unexpected error occurred. Please try again later."
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

def search_web(query: str) -> str:
    """
    Use this web search tool ONLY to retrieve REAL-TIME, UP-TO-DATE data, 
    the LATEST NEWS, or information about events that have occurred since 2023. 
    DO NOT use this tool for questions regarding history, famous people (such as Albert Einstein), 
    or widely known general knowledge.
    """
    endpoint = "https://api.duckduckgo.com/"
    params = {
        "q": query,       # Truy vấn tìm kiếm
        "format": "json", # Định dạng JSON
        "no_html": 1      # Loại bỏ HTML trong kết quả
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        data = response.json()

        # Lấy thông tin từ trường "AbstractText"
        abstract = data.get("AbstractText", "")
        if abstract:
            return abstract

        # Nếu không có "AbstractText", trả về thông báo mặc định
        return "No relevant information found for your query."
    except Exception as e:
        return f"Error during web search: {e}"

def get_weather(city: str) -> str:
    """
    Retrieves the current weather forecast. 
    
    If the user's query **does not specify a location**, the system will automatically 
    prioritize checking the weather for the robot's default location, 
    which is **Diên Hồng Ward, Ho Chi Minh City, Vietnam**. 
    
    If a specific city is provided by the user, the function must return the weather 
    for that location. 
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")

    # Đọc API key từ tệp config.json
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        api_key = config.get("openweathermap_api_key")
        if not api_key:
            return "API key for OpenWeatherMap is missing in config.json."
    except FileNotFoundError:
        return "Configuration file 'config.json' not found."
    except json.JSONDecodeError:
        return "Error decoding 'config.json'. Please check the file format."

    # URL API OpenWeatherMap
    base_url = "http://api.openweathermap.org/data/2.5/weather"

    try:
        # Gửi yêu cầu đến API
        response = requests.get(base_url, params={
            "q": city,
            "appid": api_key,
            "units": "metric",  # Đơn vị nhiệt độ: Celsius
            "lang": "en"        # Ngôn ngữ: tiếng Anh
        })
            
        # Kiểm tra trạng thái phản hồi
        if response.status_code == 200:
            data = response.json()
            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]

            # Trả về chuỗi mô tả thời tiết
            return (f"The weather in {city} is currently '{weather_description}' with a temperature of {temperature}°C. "
                    f"It feels like {feels_like}°C with a humidity of {humidity}%.")
        elif response.status_code == 404:
            return f"City '{city}' not found. Please check the city name."
        else:
            return f"Error fetching weather data: {response.status_code} - {response.reason}"
    except requests.RequestException as e:
        return f"An error occurred while fetching weather data: {e}"
    

