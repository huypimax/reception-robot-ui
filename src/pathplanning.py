from mqtt.publish_waypoints import WaypointsPublisher 
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mqtt.subcribe_location import LocationSubscriberThread
from mqtt_manager import MQTTConfig, BaseManager

LOCATION_CONFIG = MQTTConfig.get_config("location")

class LocationManager(BaseManager):
    def __init__(self, ui):
        super().__init__(ui, LocationSubscriberThread, LOCATION_CONFIG)
        # Giá trị mặc định ban đầu
        self.location = {'x': '0.0', 'y': '0.0', 'theta': '0.0'}

    def _connect_signals(self):
        self.subscriber_thread.location_update.connect(self.handle_data_update)

    def start_location_subscriber(self):
        self.start_subscriber()

    def stop_location_subscriber(self):
        self.stop_subscriber()

    def handle_data_update(self, x, y, theta):
        self.location = {
            'x': f"{x:.1f}",
            'y': f"{y:.1f}",
            'theta': f"{theta:.1f}"
        }


    def send_waypoint(self, place: str):
        """
        Gửi danh sách waypoint tương ứng với place qua MQTT.
        """
        # Fake dữ liệu waypoint (x, y, heading)
        waypoint_data = {
            "Electrical lab": [
                {"x": 0.0, "y": 0.0, "yaw": 0.0},
                {"x": 1.2, "y": 0.5, "yaw": 0.0},
                {"x": 2.5, "y": 0.7, "yaw": 1.57}
            ],
            "Robotics lab": [
                {"x": 0.0, "y": 0.0, "yaw": 0.0},
                {"x": -1.5, "y": 0.6, "yaw": -1.57},
                {"x": -2.5, "y": 1.2, "yaw": -3.14}
            ],
            "Chemistry Hall": [
                {"x": 0.0, "y": 0.0, "yaw": 0.0},
                {"x": 0.8, "y": -1.0, "yaw": 3.14}
            ],
            "Man restroom": [
                {"x": 0.0, "y": 0.0, "yaw": 0.0},
                {"x": 0.5, "y": 0.5, "yaw": 1.57},
                {"x": 1.0, "y": 1.0, "yaw": 1.57}
            ]
        }

        if place not in waypoint_data:
            print(f"[WARN] No waypoint for {place}")
            return

        current_wp = {
                "x": float(self.location["x"]),
                "y": float(self.location["y"]),
            }

        full_wp_list = [current_wp] + waypoint_data[place]

        waypoints_json = json.dumps(full_wp_list, indent=2)

        publisher = WaypointsPublisher()
        publisher.publish_waypoints(waypoints_json)
        print(f"Waypoints in /map coordinates (JSON): {waypoints_json}")