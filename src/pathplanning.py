from mqtt.publish_goal import GoalPublisher 
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
    def __init__(self, ui, arrival_manager):
        super().__init__(ui, LocationSubscriberThread, LOCATION_CONFIG)
        self.location = {'x': '0.0', 'y': '0.0', 'theta': '0.0'}
        self.arrival_manager = arrival_manager  # Reference to ArrivalManager for checking arrival

    def _connect_signals(self):
        self.subscriber_thread.location_update.connect(self.handle_location_update)

    def start_location_subscriber(self):
        self.start_subscriber()

    def stop_location_subscriber(self):
        self.stop_subscriber()

    def handle_location_update(self, x, y, theta):
        self.location = {'x': f"{x:.2f}", 'y': f"{y:.2f}", 'theta': f"{theta:.1f}"}

    def send_goal(self, place: str):
        goal_json = json.dumps(place)
        print(f"Goal in /map coordinates (JSON): {goal_json}")
        publisher = GoalPublisher()
        publisher.publish_goal(goal_json)
