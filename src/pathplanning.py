from mqtt.publish_waypoints import WaypointsPublisher 
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mqtt.subscribe_location import LocationSubscriberThread
from mqtt.subscribe_arrival import ArrivalSubscriberThread
from mqtt_manager import MQTTConfig, BaseManager

LOCATION_CONFIG = MQTTConfig.get_config("location")
ARRIVAL_CONFIG = MQTTConfig.get_config("arrival")

class ArrivalManager(BaseManager):
    def __init__(self, ui):
        super().__init__(ui, ArrivalSubscriberThread, ARRIVAL_CONFIG)
        self.arrival = "false"

    def _connect_signals(self):
        self.subscriber_thread.arrival_update.connect(self.handle_arrival_update)

    def start_arrival_subscriber(self):
        self.start_subscriber()

    def stop_arrival_subscriber(self):
        self.stop_subscriber()

    def handle_arrival_update(self, arrived):
        self.arrival = arrived
        return arrived
        
class LocationManager(BaseManager):
    def __init__(self, ui):
        super().__init__(ui, LocationSubscriberThread, LOCATION_CONFIG)
        self.location = {'x': '0.0', 'y': '0.0', 'theta': '0.0'}

    def _connect_signals(self):
        self.subscriber_thread.location_update.connect(self.handle_location_update)

    def start_location_subscriber(self):
        self.start_subscriber()

    def stop_location_subscriber(self):
        self.stop_subscriber()

    def handle_location_update(self, x, y, theta):
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
                {
                    "x": 10.04,
                    "y": 16.72
                },
                {
                    "x": 21.54,
                    "y": 35.22
                }
                ],
            "Robotics lab": [
                {
                    "x": 8.69,
                    "y": 13.97
                },
                {
                    "x": 0.14,
                    "y": -0.03
                }
                ],
            "Chemistry Hall": [
                {
                    "x": 1.64,
                    "y": 19.72
                },
                {
                    "x": -1.46,
                    "y": 22.82
                },
                {
                    "x": -1.21,
                    "y": 25.02
                },
                {
                    "x": -5.16,
                    "y": 27.62
                }
                ],
            "Restroom": [
                {
                    "x": 3.54,
                    "y": 19.72
                },
                {
                    "x": -3.21,
                    "y": 21.87
                }
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

