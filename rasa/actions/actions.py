# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

class ActionGetWeather(Action):
    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Ví dụ: cố định tọa độ trường (thay bằng tọa độ thực tế)
        lat = 10.762622
        lon = 106.660172
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            cw = data.get("current_weather", {})
            temp = cw.get("temperature")
            wind = cw.get("windspeed")
            text = f"Hiện tại nhiệt độ khoảng {temp}°C, gió {wind} km/h."
        except Exception as e:
            text = "Mình không lấy được dữ liệu thời tiết ngay bây giờ."

        dispatcher.utter_message(text=text)
        return []
