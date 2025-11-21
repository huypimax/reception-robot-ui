from mqtt.publish_waypoints import WaypointsPublisher 
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mqtt.subscribe_location import LocationSubscriberThread
from mqtt.subscribe_arrival import ArrivalSubscriberThread
from mqtt_manager import MQTTConfig, BaseManager

import csv
import time
import threading
import numpy as np
import datetime

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
        self.logging_thread = None
        self.log_data = []  # To store log entries (time, plan_x, plan_y, actual_x, actual_y, error)
        self.plan_points = []  # Planned waypoints (full list, will pop as robot progresses)
        self.threshold_to_next = 0.3  # Distance threshold to shift to next waypoint (in meters)

    def _connect_signals(self):
        self.subscriber_thread.location_update.connect(self.handle_location_update)

    def start_location_subscriber(self):
        self.start_subscriber()

    def stop_location_subscriber(self):
        self.stop_subscriber()

    def handle_location_update(self, x, y, theta):
        self.location = {'x': f"{x:.2f}", 'y': f"{y:.2f}", 'theta': f"{theta:.1f}"}

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
                    "x": 16.875,
                    "y": 12.409
                },
                {
                    "x": 19.968,
                    "y": 14.454
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

        self.plan_points = [current_wp] + waypoint_data[place]

        full_wp_list = self.plan_points

        waypoints_json = json.dumps(full_wp_list, indent=2)

        print(f"Waypoints in /map coordinates (JSON): {waypoints_json}")
        publisher = WaypointsPublisher()
        publisher.publish_waypoints(waypoints_json)

        # Start logging after sending waypoints
        self.start_logging()

    def start_logging(self):
        """Start a background thread to log data until arrival is true."""
        if self.logging_thread is None or not self.logging_thread.is_alive():
            self.log_data = []
            self.logging_thread = threading.Thread(target=self.logging_loop)
            self.logging_thread.start()

    def logging_loop(self):
        """Loop to sample actual positions every second until arrival is true."""
        if len(self.plan_points) < 2:
            print("No more waypoints to process.")
            return 

        actual_x = float(self.location['x'])
        actual_y = float(self.location['y'])
        timestamp = datetime.datetime.now()

        # Calculate CTE
        p1, p2 = self.plan_points[0], self.plan_points[1]
        x1, y1 = p1["x"], p1["y"]
        x2, y2 = p2["x"], p2["y"]
        xr, yr = actual_x, actual_y

        # Vector projection for CTE
        vx, vy = x2 - x1, y2 - y1
        wx, wy = xr - x1, yr - y1
        c1 = wx * vx + wy * vy
        c2 = vx * vx + vy * vy
        t = max(0.0, min(1.0, c1 / c2 if c2 > 0 else 0.0))

        # Projected point on the line (plan_x, plan_y)
        plan_x = x1 + t * vx
        plan_y = y1 + t * vy

        # CTE error (perpendicular distance)
        error = np.hypot(xr - plan_x, yr - plan_y)

        # Log the data
        self.log_data.append((timestamp, plan_x, plan_y, actual_x, actual_y, error))

        # Shift to next segment if close to next WP
        dist_to_next = np.hypot(xr - x2, yr - y2)
        if dist_to_next < self.threshold_to_next and len(self.plan_points) > 2:
            self.plan_points.pop(0)

        time.sleep(1)  # Sample every 1 second

        # When arrival is true, write to CSV with summary
        # print ("arrival is true")
        # self.export_path_comparison()

    def export_path_comparison(self):
        if not self.plan_points:
            print("No planned path.")
            return
        if not self.log_data:
            print("Robot chưa di chuyển.")
            return

        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        full_path = f"log_path/path_comparison_{timestamp_str}.csv"

        errors = []
        with open(full_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['time', 'actual_x', 'actual_y', 'plan_x', 'plan_y', 'error_m'])

            for row in self.log_data:
                writer.writerow([
                    row[0].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    round(row[3], 3),  # actual_x
                    round(row[4], 3),  # actual_y
                    round(row[1], 3),  # plan_x
                    round(row[2], 3),  # plan_y
                    round(row[5], 3)   # error
                ])
                errors.append(row[5])

            writer.writerow([])
            if errors:
                mean_error = np.mean(errors)
                max_error = np.max(errors)
                summary = f"Avg error: {mean_error:.3f}m | Max error: {max_error:.3f}m"
                writer.writerow([summary])

        print(f"Exported: {full_path}")
        self.log_data = []  # Clear after export