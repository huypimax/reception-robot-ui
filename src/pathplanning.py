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
            'x': f"{x:.2f}",
            'y': f"{y:.2f}",
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
                    "x": 9.39,
                    "y": 16.02
                },
                {
                    "x": 21.54,
                    "y": 35.22
                }
                ],
            "Robotics lab": [
                {
                    "x": 9.39,
                    "y": 16.02
                },
                {
                    "x": 0.14,
                    "y": -0.03
                }
                ],
            "Chemistry Hall": [
                # {
                #     "x": 1.64,
                #     "y": 19.72
                # },
                {
                    "x": -2.21,
                    "y": 22.32
                },
                {
                    "x": -0.96,
                    "y": 24.47
                },
                {
                    "x": -9.51,
                    "y": 30.47
                },
                {
                    "x": -11.06,
                    "y": 31.12
                }
                ],
            "Restroom": [
                {
                    "x": -2.21,
                    "y": 22.32
                },
                {
                    "x": -4.66,
                    "y": 18.12
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

