import paho.mqtt.client as mqtt
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import time

# ==========================================
# 1. CONFIGURATION (FILL THIS IN)
# ==========================================
# Your TTN Application ID
APP_ID = "iot-janusz-app" 

# The API Key you just generated in TTN
API_KEY = "NNSXS.QUTIIBHEDG66T6QB2WW6S54ICGKMMF3G5U3LK3Y.4D5SS7LO5F5YODXJGE7L3X5KOZMF4SZU6AZVCLBSKLXEKLLKS45Q"

# Your Device ID
DEVICE_ID = "jonusz-device2-abp"

# ==========================================
# 1.5 INFLUXDB CONFIGURATION
# ==========================================
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "_OIhs2CmUHO_L119yR8iHmKRywmQejG5tHwWz08xxsXAY0TaEdertcOoXG6GlF6OA4vWEblIPXfdcNuyEW2Hxw=="
INFLUX_ORG = "itu" 
INFLUX_BUCKET = "weather baloon" 

# Initialize InfluxDB Client
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

def wait_for_influxdb(client):
    """Pings the database every 15 seconds until it responds."""
    print("Checking InfluxDB connection...")
    # client.ping() returns True if the DB is running, False if it is not
    while not client.ping():
        print("Turn on DB! (Waiting 15 seconds to try again...)")
        time.sleep(15)
    print("InfluxDB is online! Proceeding with script...\n")

# ==========================================
# 2. TTN SERVER DETAILS
# ==========================================
BROKER = "eu1.cloud.thethings.network"
PORT = 1883
TOPIC = f"v3/{APP_ID}@ttn/devices/{DEVICE_ID}/up"
USERNAME = f"{APP_ID}@ttn"
PASSWORD = API_KEY

# ==========================================
# 3. MQTT CALLBACK FUNCTIONS
# ==========================================
def on_connect(client, userdata, flags, rc):
    """Called when the script successfully connects to the TTN server."""
    local_print_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if rc == 0:
        print(f"[{local_print_time}] - Successfully connected to TTN MQTT Broker!")
        print(f"📡 Subscribing to topic: {TOPIC}")
        client.subscribe(TOPIC)
        print("⏳ Waiting for data from the balloon...\n")
    else:
        print(f"[{local_print_time}] - Connection failed with code {rc}")

def on_message(client, userdata, msg):
    """Called every time a new message arrives from the balloon."""
    local_print_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # The message arrives as a JSON string, so we parse it
        payload_json = json.loads(msg.payload.decode('utf-8'))
        
        # Extract precise time from TTN (Fallback to current time if missing)
        ttn_time_string = payload_json.get("received_at", datetime.utcnow().isoformat())
        
        # Navigate through the JSON structure
        uplink_message = payload_json.get("uplink_message", {})
        decoded_payload = uplink_message.get("decoded_payload", {})
        
        # Extract Hex and RSSI
        image_hex = decoded_payload.get("image_hex", "No hex found")
        latitude = decoded_payload.get("latitude", 0.0)    
        longitude = decoded_payload.get("longitude", 0.0)  
        altitude = decoded_payload.get("altitude", 0.0)    

        rx_metadata = uplink_message.get("rx_metadata", [{}])
        rssi = rx_metadata[0].get("rssi", 0)

        print("-" * 50)
        print(f"[{local_print_time}] - NEW BALLOON DATA RECEIVED!")
        print(f"Image Hex: {image_hex}")
        print(f"RSSI: {rssi} dBm")
        print("-" * 50)
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
        print(f"Altitude: {altitude}")
        
        # --- MISSING CODE ADDED: WRITE TO INFLUXDB ---
        if image_hex != "No hex found":
            # Create a "point" containing our data
            point = Point("balloon_telemetry") \
                .tag("device", DEVICE_ID) \
                .field("image_hex", image_hex) \
                .field("rssi", float(rssi)) \
                .field("latitude", float(latitude)) \
                .field("longitude", float(longitude)) \
                .field("altitude", float(altitude)) \
                .time(ttn_time_string) 
            
            # Send it to the database!
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
            print(f"[{local_print_time}] 💾 Successfully saved to InfluxDB!\n")
            
    except Exception as e:
        print(f"[{local_print_time}] - Error parsing message: {e}")

# ==========================================
# 4. START THE SCRIPT
# ==========================================
if __name__ == "__main__":
    
    wait_for_influxdb(influx_client)

    print("Starting Windows MQTT Client...")
    
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(BROKER, PORT, 60)
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n Disconnected by user.")
        client.disconnect()