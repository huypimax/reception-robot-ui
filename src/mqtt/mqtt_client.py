# mqtt_client.py
import paho.mqtt.client as mqtt

BROKER_ADDRESS = "192.168.0.120"  
BROKER_PORT = 1883
TOPIC_COMMAND = "robot/move"
TOPIC_STATUS = "robot/status/location"

class MQTTHandler:
    def __init__(self, on_status_update_callback):
        self.client = mqtt.Client()
        self.client.on_message = self._on_message
        self.client.connect(BROKER_ADDRESS, BROKER_PORT)
        self.client.subscribe(TOPIC_STATUS)
        self.client.loop_start()

        self.current_position = None
        self.current_target = None
        self.on_status_update_callback = on_status_update_callback

    def _on_message(self, client, userdata, msg):
        location = msg.payload.decode()
        self.current_position = location
        if self.on_status_update_callback:
            self.on_status_update_callback(location)

    def send_destination(self, dest: str):
        if dest.upper() in ["A", "B", "C", "D"]:
            self.current_target = dest.upper()
            result = self.client.publish(TOPIC_COMMAND, dest.upper())
            status = result[0]
            if status == 0:
                print(f"✅ Sent move command to room {dest.upper()}")
            else:
                print(f"❌ Failed to send move command to room {dest.upper()}, status={status}")
