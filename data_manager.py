"""Data Manager app for KitchenGuard IoT.

Responsibilities:
1. Subscribe to sensor and actuator MQTT topics.
2. Save all incoming messages into a local SQLite DB.
3. Analyze sensor values according to safety thresholds.
4. Publish Warning/Alarm messages and actuator commands when needed.
"""
from __future__ import annotations

import json

import paho.mqtt.client as mqtt

from config import (
    GAS_ALARM_THRESHOLD,
    MQTT_BROKER,
    MQTT_PORT,
    SMOKE_ALARM_THRESHOLD,
    TEMP_ALARM_THRESHOLD,
    TEMP_WARNING_THRESHOLD,
    TOPIC_ACTUATORS,
    TOPIC_ALERTS,
    TOPIC_COMMANDS,
    TOPIC_SENSORS,
    TOPIC_STATUS,
)
from database import init_db, insert_event, insert_sensor


def sensor_status(sensor: str, value: float) -> tuple[str, str, str]:
    """Return (status, severity, message)."""
    if sensor == "temperature":
        if value >= TEMP_ALARM_THRESHOLD:
            return "ALARM", "CRITICAL", "Extreme kitchen temperature detected"
        if value >= TEMP_WARNING_THRESHOLD:
            return "WARNING", "WARNING", "High kitchen temperature detected"
        return "NORMAL", "INFO", "Temperature is normal"

    if sensor == "gas":
        if value >= GAS_ALARM_THRESHOLD:
            return "ALARM", "CRITICAL", "Gas leak detected"
        return "NORMAL", "INFO", "Gas level is normal"

    if sensor == "smoke":
        if value >= SMOKE_ALARM_THRESHOLD:
            return "ALARM", "CRITICAL", "Smoke detected in kitchen"
        return "NORMAL", "INFO", "Smoke level is normal"

    return "NORMAL", "INFO", f"{sensor} value received"


def publish_json(client: mqtt.Client, topic: str, data: dict, qos: int = 1) -> None:
    client.publish(topic, json.dumps(data), qos=qos, retain=False)


def handle_alarm_actions(client: mqtt.Client, sensor: str, status: str) -> None:
    if status != "ALARM":
        return

    # Automatic safety actions: close gas valve, turn fan on, activate alarm.
    commands = [
        {"target": "gas_valve", "state": "closed", "reason": sensor},
        {"target": "fan", "state": "on", "reason": sensor},
        {"target": "alarm", "state": "on", "reason": sensor},
    ]
    for command in commands:
        publish_json(client, TOPIC_COMMANDS, command)


def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Data Manager connected to MQTT broker")
    client.subscribe([(TOPIC_SENSORS, 1), (TOPIC_ACTUATORS, 1)])
    insert_event("SYSTEM", "Data Manager connected to MQTT broker", "INFO")
    publish_json(client, TOPIC_STATUS, {"component": "data_manager", "status": "online"})


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        print("Invalid JSON message:", msg.payload)
        return

    print(f"Received on {msg.topic}: {data}")

    if msg.topic == TOPIC_SENSORS:
        sensor = data.get("sensor", "unknown")
        value = float(data.get("value", 0))
        unit = data.get("unit", "")
        status, severity, message = sensor_status(sensor, value)

        insert_sensor(sensor, value, unit, status, json.dumps(data))
        insert_event(sensor.upper(), f"{message}: {value}{unit}", severity)

        alert = {
            "sensor": sensor,
            "value": value,
            "unit": unit,
            "status": status,
            "severity": severity,
            "message": message,
        }
        publish_json(client, TOPIC_ALERTS, alert)
        handle_alarm_actions(client, sensor, status)

    elif msg.topic == TOPIC_ACTUATORS:
        insert_event("ACTUATOR", f"Actuator update: {data.get('state')}", "INFO")


def main() -> None:
    init_db()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="omer_data_manager")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    print("Data Manager started")
    print("Listening to topics:")
    print(" -", TOPIC_SENSORS)
    print(" -", TOPIC_ACTUATORS)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        insert_event("SYSTEM", "Data Manager stopped", "INFO")
        client.disconnect()
        print("Data Manager stopped")


if __name__ == "__main__":
    main()
