"""Gas and smoke sensor emulator: publishes safety values to MQTT."""
from __future__ import annotations

import json
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt

from config import MQTT_BROKER, MQTT_PORT, TOPIC_SENSORS, PUBLISH_INTERVAL_SECONDS


def create_message(sensor: str) -> dict:
    if sensor == "gas":
        value = random.choice([random.uniform(3, 18), random.uniform(55, 85)])
        unit = "%"
        device_id = "MQ2-GAS-01"
    else:
        value = random.choice([random.uniform(1, 12), random.uniform(45, 78)])
        unit = "%"
        device_id = "SMOKE-01"

    return {
        "device_id": device_id,
        "type": "sensor",
        "sensor": sensor,
        "value": round(value, 1),
        "unit": unit,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def main() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="omer_gas_smoke_emulator")
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()

    print(f"Gas/Smoke emulator started. Publishing to: {TOPIC_SENSORS}")
    try:
        while True:
            for sensor in ("gas", "smoke"):
                message = create_message(sensor)
                payload = json.dumps(message)
                client.publish(TOPIC_SENSORS, payload, qos=1, retain=False)
                print("Published:", payload)
                time.sleep(1)
            time.sleep(PUBLISH_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("Gas/Smoke emulator stopped")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
