"""Small helper to print recent SQLite DB records."""
from database import init_db, latest_events, latest_sensor_values

init_db()
print("Latest sensor values:")
for sensor, data in latest_sensor_values().items():
    print(sensor, data)

print("\nRecent events:")
for event in latest_events(20):
    print(dict(event))
