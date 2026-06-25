"""DHT-like temperature emulator: publishes kitchen temperature values to MQTT."""
from __future__ import annotations

import json
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt

from config import MQTT_BROKER, MQTT_PORT, TOPIC_SENSORS, PUBLISH_INTERVAL_SECONDS


def create_message() -> dict:
    # Mostly normal values, sometimes high values to demonstrate warning logic.
    value = random.choice([random.uniform(22, 32), random.uniform(38, 55)])
    return {
        "device_id": "DHT22-KITCHEN-01",
        "type": "sensor",
        "sensor": "temperature",
        "value": round(value, 1),
        "unit": "C",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def main() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="omer_temperature_emulator")
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()

    print(f"Temperature emulator started. Publishing to: {TOPIC_SENSORS}")
    try:
        while True:
            message = create_message()
            payload = json.dumps(message)
            client.publish(TOPIC_SENSORS, payload, qos=1, retain=False)
            print("Published:", payload)
            time.sleep(PUBLISH_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("Temperature emulator stopped")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
