"""Button/Relay actuator emulator.

This program subscribes to command messages and simulates physical actuators:
fan relay, gas valve relay, and alarm buzzer. It also publishes current actuator state.
"""
from __future__ import annotations

import json
import time
from datetime import datetime

import paho.mqtt.client as mqtt

from config import MQTT_BROKER, MQTT_PORT, TOPIC_ACTUATORS, TOPIC_COMMANDS

state = {
    "fan": "off",
    "gas_valve": "open",
    "alarm": "off",
}


def publish_state(client: mqtt.Client, action: str = "state_update") -> None:
    payload = json.dumps(
        {
            "device_id": "KITCHEN-RELAY-BOARD-01",
            "type": "actuator",
            "action": action,
            "state": state,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
    )
    client.publish(TOPIC_ACTUATORS, payload, qos=1, retain=False)
    print("Actuator state:", payload)


def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Actuator connected to MQTT broker")
    client.subscribe(TOPIC_COMMANDS, qos=1)
    publish_state(client)


def on_message(client, userdata, msg):
    try:
        command = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        print("Invalid command:", msg.payload)
        return

    target = command.get("target")
    new_state = command.get("state")

    if target in state and new_state in {"on", "off", "open", "closed"}:
        state[target] = new_state
        publish_state(client, action=f"set_{target}_{new_state}")
    else:
        print("Unknown command:", command)


def main() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="omer_actuator_emulator")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    print(f"Actuator emulator started. Listening to: {TOPIC_COMMANDS}")
    client.loop_start()
    try:
        while True:
            publish_state(client)
            time.sleep(10)
    except KeyboardInterrupt:
        print("Actuator emulator stopped")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
