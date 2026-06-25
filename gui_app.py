"""Main GUI app for KitchenGuard IoT.

Shows live sensor values, warnings/alarms, actuator status and recent events.
"""
from __future__ import annotations

import json
import queue
import threading
import tkinter as tk
from tkinter import ttk

import paho.mqtt.client as mqtt

from config import MQTT_BROKER, MQTT_PORT, TOPIC_ACTUATORS, TOPIC_ALERTS, TOPIC_COMMANDS, TOPIC_STATUS
from database import init_db, latest_events, latest_sensor_values

message_queue: queue.Queue[tuple[str, dict]] = queue.Queue()


def publish_command(target: str, state: str) -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"omer_gui_command_{target}")
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()
    client.publish(TOPIC_COMMANDS, json.dumps({"target": target, "state": state, "source": "gui"}), qos=1)
    client.loop_stop()
    client.disconnect()


class SmartKitchenGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("KitchenGuard IoT - Main GUI")
        self.geometry("920x620")
        self.configure(bg="#eef3f8")

        self.status_var = tk.StringVar(value="System loading...")
        self.sensor_vars = {
            "temperature": tk.StringVar(value="-- °C"),
            "gas": tk.StringVar(value="-- %"),
            "smoke": tk.StringVar(value="-- %"),
        }
        self.actuator_var = tk.StringVar(value="Fan: -- | Gas valve: -- | Alarm: --")
        self.alert_var = tk.StringVar(value="No alerts yet")

        self._build_ui()
        self.refresh_from_db()
        self.after(700, self.process_mqtt_queue)
        self.after(3000, self.periodic_db_refresh)

    def _build_ui(self) -> None:
        title = tk.Label(self, text="KitchenGuard IoT Dashboard", font=("Arial", 24, "bold"), bg="#eef3f8", fg="#0f172a")
        title.pack(pady=(18, 4))

        subtitle = tk.Label(self, text="Main GUI app: live data, warnings and alarm status", font=("Arial", 12), bg="#eef3f8", fg="#475569")
        subtitle.pack(pady=(0, 14))

        status = tk.Label(self, textvariable=self.status_var, font=("Arial", 14, "bold"), bg="#dcfce7", fg="#166534", padx=16, pady=10)
        status.pack(pady=8)
        self.status_label = status

        sensor_frame = tk.Frame(self, bg="#eef3f8")
        sensor_frame.pack(fill="x", padx=25, pady=14)

        for sensor, label, icon in [
            ("temperature", "Temperature", "🌡️"),
            ("gas", "Gas Level", "🔥"),
            ("smoke", "Smoke Level", "💨"),
        ]:
            card = tk.Frame(sensor_frame, bg="white", padx=20, pady=16, highlightbackground="#dbe3ef", highlightthickness=1)
            card.pack(side="left", expand=True, fill="x", padx=8)
            tk.Label(card, text=icon, font=("Arial", 26), bg="white").pack()
            tk.Label(card, text=label, font=("Arial", 13, "bold"), bg="white", fg="#334155").pack(pady=5)
            tk.Label(card, textvariable=self.sensor_vars[sensor], font=("Arial", 23, "bold"), bg="white", fg="#0f172a").pack()

        actuator = tk.Label(self, textvariable=self.actuator_var, font=("Arial", 13, "bold"), bg="white", fg="#0f172a", padx=14, pady=12)
        actuator.pack(fill="x", padx=35, pady=10)

        controls = tk.Frame(self, bg="#eef3f8")
        controls.pack(pady=10)
        ttk.Button(controls, text="Turn Fan ON", command=lambda: publish_command("fan", "on")).grid(row=0, column=0, padx=7, pady=5)
        ttk.Button(controls, text="Close Gas Valve", command=lambda: publish_command("gas_valve", "closed")).grid(row=0, column=1, padx=7, pady=5)
        ttk.Button(controls, text="Activate Alarm", command=lambda: publish_command("alarm", "on")).grid(row=0, column=2, padx=7, pady=5)
        ttk.Button(controls, text="Reset Alarm", command=lambda: publish_command("alarm", "off")).grid(row=0, column=3, padx=7, pady=5)

        alert = tk.Label(self, textvariable=self.alert_var, font=("Arial", 13, "bold"), bg="#f8fafc", fg="#0f172a", padx=14, pady=12)
        alert.pack(fill="x", padx=35, pady=10)

        tk.Label(self, text="Recent DB Events", font=("Arial", 15, "bold"), bg="#eef3f8", fg="#0f172a").pack(pady=(12, 5))
        self.events_text = tk.Text(self, height=10, font=("Consolas", 10), bg="#0f172a", fg="#e2e8f0", padx=12, pady=12)
        self.events_text.pack(fill="both", expand=True, padx=35, pady=(0, 25))

    def set_system_status(self, text: str, severity: str = "INFO") -> None:
        self.status_var.set(text)
        if severity == "CRITICAL":
            self.status_label.configure(bg="#fee2e2", fg="#991b1b")
        elif severity == "WARNING":
            self.status_label.configure(bg="#ffedd5", fg="#9a3412")
        else:
            self.status_label.configure(bg="#dcfce7", fg="#166534")

    def refresh_from_db(self) -> None:
        values = latest_sensor_values()
        for sensor, unit_default in [("temperature", "C"), ("gas", "%"), ("smoke", "%")]:
            if sensor in values:
                row = values[sensor]
                unit = row.get("unit") or unit_default
                self.sensor_vars[sensor].set(f"{row['value']} {unit}")

        events = latest_events(10)
        self.events_text.delete("1.0", tk.END)
        for event in events:
            line = f"{event['timestamp']} | {event['severity']} | {event['event_type']} | {event['message']}\n"
            self.events_text.insert(tk.END, line)

    def periodic_db_refresh(self) -> None:
        self.refresh_from_db()
        self.after(3000, self.periodic_db_refresh)

    def process_mqtt_queue(self) -> None:
        while not message_queue.empty():
            topic, data = message_queue.get()
            if topic == TOPIC_ALERTS:
                severity = data.get("severity", "INFO")
                status = data.get("status", "NORMAL")
                text = f"{status}: {data.get('message')} ({data.get('value')} {data.get('unit')})"
                self.alert_var.set(text)
                self.set_system_status(text, severity)
            elif topic == TOPIC_ACTUATORS:
                state = data.get("state", {})
                self.actuator_var.set(
                    f"Fan: {state.get('fan', '--')} | Gas valve: {state.get('gas_valve', '--')} | Alarm: {state.get('alarm', '--')}"
                )
            elif topic == TOPIC_STATUS:
                self.set_system_status(f"Status: {data}", "INFO")
        self.after(700, self.process_mqtt_queue)


def mqtt_thread() -> None:
    def on_connect(client, userdata, flags, reason_code, properties=None):
        client.subscribe([(TOPIC_ALERTS, 1), (TOPIC_ACTUATORS, 1), (TOPIC_STATUS, 1)])

    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
        except json.JSONDecodeError:
            return
        message_queue.put((msg.topic, data))

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="omer_main_gui")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_forever()


def main() -> None:
    init_db()
    threading.Thread(target=mqtt_thread, daemon=True).start()
    app = SmartKitchenGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
