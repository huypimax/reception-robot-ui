"""
MQTT - Manager Configuration file
Quản lý các thông số MQTT để tránh hard-code ở nhiều nơi
Base class cho các manager để tránh code trùng lắp
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class MQTTConfig:
    """Class chứa tất cả cấu hình MQTT"""
    
    MQTT_HOST = "45.117.177.157" #127.0.0.1 #192.168.0.130
    MQTT_PORT = 1883
    MQTT_KEEPALIVE = 60
    MQTT_USERNAME = "client"
    MQTT_PASSWORD = "viam1234"
    
    # Các MQTT Topics
    TOPICS = {
        "attendance": "robot/attendance",
        "status": "robot/status",
        "location": "robot/location",
        "waypoints" : "robot/waypoints"
    }
    
    @classmethod
    def get_config(cls, topic_name):
        """
        Lấy cấu hình MQTT cho một topic cụ thể
        
        Args:
            topic_name (str): Tên topic cần lấy config
            
        Returns:
            dict: Dictionary chứa mqtt_host, mqtt_port, mqtt_topic, mqtt_username, mqtt_password
        """
        if topic_name not in cls.TOPICS:
            raise ValueError(f"Topic '{topic_name}' không tồn tại. Available topics: {list(cls.TOPICS.keys())}")
            
        return {
            "mqtt_host": cls.MQTT_HOST,
            "mqtt_port": cls.MQTT_PORT,
            "mqtt_topic": cls.TOPICS[topic_name],
            "mqtt_username": cls.MQTT_USERNAME,
            "mqtt_password": cls.MQTT_PASSWORD
        }
    
    @classmethod
    def get_all_configs(cls):
        """Lấy tất cả config cho các topic"""
        return {topic: cls.get_config(topic) for topic in cls.TOPICS.keys()}
    
    @classmethod
    def update_host(cls, new_host):
        """Cập nhật MQTT host"""
        cls.MQTT_HOST = new_host
        print(f"MQTT Host updated to: {new_host}")
    
    @classmethod
    def update_port(cls, new_port):
        """Cập nhật MQTT port"""
        cls.MQTT_PORT = new_port
        print(f"MQTT Port updated to: {new_port}")
    
    @classmethod
    def update_credentials(cls, username, password):
        """Cập nhật MQTT username và password"""
        cls.MQTT_USERNAME = username
        cls.MQTT_PASSWORD = password
        print(f"MQTT credentials updated for user: {username}")
        
    @classmethod
    def add_topic(cls, topic_name, topic_path):
        """Thêm topic mới"""
        cls.TOPICS[topic_name] = topic_path
        print(f"Added new topic: {topic_name} -> {topic_path}")

# Các default configs cho từng loại manager
ATTENDANCE_CONFIG = MQTTConfig.get_config("attendance")
LOCATION_CONFIG = MQTTConfig.get_config("location")

class BaseManager:
    """Base class cho các manager để tránh code trùng lắp"""
    
    def __init__(self, ui, subscriber_class, mqtt_config):
        self.ui = ui
        self.subscriber_class = subscriber_class
        self.mqtt_config = mqtt_config
        self.subscriber_thread = None
        self.is_running = False
        
    def start_subscriber(self):
        """Khởi tạo và bắt đầu subscriber thread"""
        if not hasattr(self, "subscriber_thread") or self.subscriber_thread is None:
            self.subscriber_thread = self.subscriber_class(**self.mqtt_config)
            self._connect_signals()
            self.subscriber_thread.start()
            self.is_running = True
            print(f"{self.__class__.__name__} subscriber started")

    def stop_subscriber(self):
        """Dừng subscriber thread"""
        if self.subscriber_thread:
            self.subscriber_thread.stop()
            self.subscriber_thread = None
            self.is_running = False
            print(f"{self.__class__.__name__} subscriber stopped")
            
    def restart_subscriber(self):
        """Khởi động lại subscriber (hữu ích khi thay đổi config)"""
        print(f"Restarting {self.__class__.__name__} subscriber...")
        self.stop_subscriber()
        self.start_subscriber()

    def update_mqtt_config(self, new_config):
        """Cập nhật config MQTT và khởi động lại subscriber nếu đang chạy"""
        was_running = self.is_running
        if was_running:
            self.stop_subscriber()
        
        self.mqtt_config = new_config
        print(f"Updated MQTT config for {self.__class__.__name__}: {new_config}")
        
        if was_running:
            self.start_subscriber()

    def _connect_signals(self):
        """Kết nối signals - sẽ được override bởi lớp con"""
        self.mqtt_status = "connected"
        self.ui.label_mqtt.setText(self.mqtt_status)
        self.ui.label_mqtt_2.setText(self.mqtt_status)
        self.ui.label_mqtt_3.setText(self.mqtt_status)
        raise NotImplementedError("Subclass must implement _connect_signals method")

    def handle_data_update(self, data):
        """Xử lý dữ liệu nhận được - sẽ được override bởi lớp con"""
        raise NotImplementedError("Subclass must implement handle_data_update method")

    def is_subscriber_running(self):
        """Kiểm tra trạng thái subscriber"""
        return self.is_running
        
    def get_current_config(self):
        """Lấy config hiện tại"""
        return self.mqtt_config.copy()