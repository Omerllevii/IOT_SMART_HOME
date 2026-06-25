"""Shared configuration for KitchenGuard IoT project."""

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

# Unique prefix prevents collisions with other students using the public HiveMQ broker.
TOPIC_PREFIX = "omer_levi_iot_smart_kitchen"

TOPIC_SENSORS = f"{TOPIC_PREFIX}/sensors"
TOPIC_ACTUATORS = f"{TOPIC_PREFIX}/actuators"
TOPIC_COMMANDS = f"{TOPIC_PREFIX}/commands"
TOPIC_ALERTS = f"{TOPIC_PREFIX}/alerts"
TOPIC_STATUS = f"{TOPIC_PREFIX}/status"

DB_FILE = "smart_kitchen.db"

TEMP_WARNING_THRESHOLD = 40
TEMP_ALARM_THRESHOLD = 50
GAS_ALARM_THRESHOLD = 60
SMOKE_ALARM_THRESHOLD = 50
PUBLISH_INTERVAL_SECONDS = 3
