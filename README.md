# KitchenGuard IoT - Smart Kitchen Monitoring System

IoT course project by Omer Levi.

The project simulates a smart kitchen safety system using MQTT, Python emulators, a data manager, SQLite local database, a Python GUI and a web demo dashboard.

## Project Goals

The system monitors kitchen safety conditions and reacts to dangerous events such as gas leak, smoke and high temperature.

## Architecture

```text
Temperature Emulator  --->
Gas/Smoke Emulator    --->  MQTT Broker  --->  Data Manager  --->  SQLite DB
Actuator Emulator     <---                 --->  Alerts/Commands ---> GUI App

Web Demo: demo.html published with GitHub Pages
```

## Components

### 1. Emulators

- `temperature_emulator.py` - DHT-like temperature sensor producer.
- `gas_smoke_emulator.py` - gas and smoke data producer.
- `actuator_emulator.py` - relay/button actuator emulator for fan, gas valve and alarm.

### 2. Data Manager

- `data_manager.py`
- Subscribes to MQTT sensor topics.
- Saves all data to SQLite local DB.
- Processes messages and detects Warning/Alarm states.
- Publishes alerts and automatic actuator commands.

### 3. Main GUI App

- `gui_app.py`
- Shows live sensor values.
- Shows Info/Warning/Alarm status.
- Shows actuator state and recent DB events.
- Allows manual control commands.

### 4. Local Database

- SQLite DB file: `smart_kitchen.db`
- Tables:
  - `sensor_data`
  - `events`

### 5. Web Demo

- `demo.html`
- Interactive GitHub Pages dashboard demo.

## MQTT Configuration

Broker:

```text
broker.hivemq.com:1883
```

Topics:

```text
omer_levi_iot_smart_kitchen/sensors
omer_levi_iot_smart_kitchen/actuators
omer_levi_iot_smart_kitchen/commands
omer_levi_iot_smart_kitchen/alerts
omer_levi_iot_smart_kitchen/status
```

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run each component in a separate terminal:

```bash
python data_manager.py
python actuator_emulator.py
python temperature_emulator.py
python gas_smoke_emulator.py
python gui_app.py
```

Or run all components together:

```bash
python run_all.py
```

To view DB records:

```bash
python view_db.py
```

## Alarm Logic

- Temperature >= 40°C: Warning
- Temperature >= 50°C: Alarm
- Gas >= 60%: Alarm
- Smoke >= 50%: Alarm

When an alarm occurs, the data manager sends automatic commands:

```text
close gas valve
turn fan on
activate alarm
```

## Course Requirements Mapping

| Requirement | Implementation |
|---|---|
| Three emulator types | Temperature sensor, gas/smoke sensor, actuator relay/button |
| Data manager app | `data_manager.py` |
| Main GUI app | `gui_app.py` |
| Local DB | SQLite `smart_kitchen.db` |
| Web demo | `demo.html` |
| GitHub repository | This repository |

## GitHub Pages Demo

```text
https://omerllevii.github.io/IOT_SMART_HOME/demo.html
```
