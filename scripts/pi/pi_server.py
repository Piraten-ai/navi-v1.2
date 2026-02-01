#!/usr/bin/env python3
"""
AADS Pi Server (Standalone)
Integrates:
1. Web Server (Frontend)
2. Sense HAT Face Control (Navi)
3. Sense HAT Sensors -> Signal K
4. MQTT Bridge (Tablet Kiosk -> Signal K)
"""

import os
import json
import time
import threading
import math
import requests
import paho.mqtt.client as mqtt
import websocket
from http.server import HTTPServer, SimpleHTTPRequestHandler, ThreadingHTTPServer
from sense_hat import SenseHat

# Configuration
PORT = 8000
SIGNALK_URL = "http://localhost:3000/signalk/v1/api/vessels/self"
WEB_ROOT = "/home/navi/AADS/frontend-web"

# Auth Token (Generated for admin, 10y)
SIGNALK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImFkbWluIiwiaWF0IjoxNzY5ODk1NDA5LCJleHAiOjIwODU0NzE0MDl9.8cYmBllXpKHaECClRabWjOt9zetMKhOi253CVCdgM06Y"

# Initialize Sense HAT
try:
    sense = SenseHat()
    sense.low_light = True
except:
    sense = None
    print("Sense HAT not found - running in emulation mode")

# Global State
current_face = "neutral"
brightness = 0.4
stop_event = threading.Event()
signalk_ws = None
signalk_lock = threading.Lock()

def dim(r, g, b):
    return (int(r * brightness), int(g * brightness), int(b * brightness))

# Define colors
O = (0, 0, 0)
C = (0, 255, 255)
G = (0, 255, 0)
R = (255, 0, 0)
Y = (255, 200, 0)
B = (0, 100, 255)

# Faces
FACES = {
    "neutral": [
        O,O,O,O,O,O,O,O, O,C,C,O,O,C,C,O, O,C,C,O,O,C,C,O, O,O,O,O,O,O,O,O,
        O,O,O,O,O,O,O,O, O,C,O,O,O,O,C,O, O,O,C,C,C,C,O,O, O,O,O,O,O,O,O,O
    ],
    "happy": [
        O,O,O,O,O,O,O,O, O,G,G,O,O,G,G,O, O,G,G,O,O,G,G,O, O,O,O,O,O,O,O,O,
        O,O,O,O,O,O,O,O, G,O,O,O,O,O,O,G, O,G,O,O,O,O,G,O, O,O,G,G,G,G,O,O
    ],
    "alert": [
        R,O,O,O,O,O,O,R, O,R,R,O,O,R,R,O, O,R,R,O,O,R,R,O, O,O,O,O,O,O,O,O,
        O,O,O,R,R,O,O,O, O,O,R,O,O,R,O,O, O,R,O,O,O,O,R,O, R,O,O,O,O,O,O,R
    ],
    "thinking": [
        O,O,O,O,O,O,O,O, O,Y,Y,O,O,O,O,O, O,Y,Y,O,O,Y,Y,O, O,Y,Y,O,O,O,Y,O,
        O,O,O,O,O,O,O,O, O,O,O,O,O,O,O,O, O,O,Y,Y,Y,O,O,O, O,O,O,O,O,O,O,O
    ],
}

def set_face(name):
    global current_face
    if sense and name in FACES:
        pixels = [dim(*p) for p in FACES[name]]
        sense.set_pixels(pixels)
        current_face = name

def datetime_iso():
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"

# --- Signal K WebSocket Connection ---
def connect_signalk_ws():
    global signalk_ws
    try:
        print("Connecting to Signal K WebSocket...")
        signalk_ws = websocket.WebSocketApp(
            "ws://localhost:3000/signalk/v1/stream?subscribe=all",
            on_error=lambda ws, err: print(f"SignalK WS Error: {err}"),
            on_close=lambda ws, close_status_code, close_msg: print("SignalK WS closed")
        )
        signalk_ws.run_forever(reconnect=5)
    except Exception as e:
        print(f"SignalK WebSocket connection failed: {e}")

def send_to_signalk(delta):
    """Send delta to Signal K via WebSocket or fallback to HTTP"""
    global signalk_ws
    try:
        if signalk_ws and signalk_ws.sock and signalk_ws.sock.connected:
            with signalk_lock:
                signalk_ws.send(json.dumps(delta))
        else:
            # Fallback to HTTP
            headers = {"Authorization": f"Bearer {SIGNALK_TOKEN}", "Content-Type": "application/json"}
            requests.post(f"{SIGNALK_URL}/delta", json=delta, headers=headers, timeout=0.5)
    except Exception as e:
        print(f"Send to SignalK failed: {e}")

# --- MQTT Handler ---
def on_mqtt_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"MQTT Rx: {msg.topic} = {payload}")
        data = json.loads(payload)

        updates = []

        # Lat/Lon
        lat = data.get('lat') or data.get('latitude')
        lon = data.get('lon') or data.get('longitude')

        if lat is not None and lon is not None:
            updates.append({
                "path": "navigation.position",
                "value": {"latitude": float(lat), "longitude": float(lon)}
            })
            print(f"  → GPS: {lat}, {lon}")

        # Speed (m/s)
        spd = data.get('speed') or data.get('spd') or data.get('sog')
        if spd is not None:
             updates.append({"path": "navigation.speedOverGround", "value": float(spd)})
             print(f"  → Speed: {spd} m/s")

        # Bearing (deg) -> Signal K (rad)
        course = data.get('bearing') or data.get('course') or data.get('cog')
        if course is not None:
            updates.append({"path": "navigation.courseOverGroundTrue", "value": float(course) * (math.pi / 180.0)})
            print(f"  → Course: {course}°")

        if updates:
            delta = {
                "context": "vessels.self",
                "updates": [{
                    "source": {"label": "tablet-mqtt"},
                    "timestamp": datetime_iso(),
                    "values": updates
                }]
            }
            send_to_signalk(delta)

    except Exception as e:
        print(f"MQTT Bridge Error: {e}")

def run_mqtt():
    try:
        print("Starting MQTT Bridge...")
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_message = on_mqtt_message
        client.connect("127.0.0.1", 1883, 60)
        client.subscribe("#") # DEBUG: Listen to EVERYTHING
        client.loop_start()
    except Exception as e:
        print(f"MQTT init failed: {e}")

# --- Sensor Loop ---
def sensor_loop():
    print("Starting Sensor Loop...")
    while not stop_event.is_set():
        if sense:
            try:
                temp = sense.get_temperature()
                press = sense.get_pressure()
                humid = sense.get_humidity() 
                orient = sense.get_orientation_radians()
                pitch = orient['pitch']
                roll = orient['roll']
                yaw = orient['yaw']

                updates = [
                    {"path": "environment.inside.temperature", "value": temp + 273.15},
                    {"path": "environment.inside.pressure", "value": press * 100},
                    {"path": "environment.inside.humidity", "value": humid / 100.0},
                    {"path": "navigation.attitude", "value": {"roll": roll, "pitch": pitch, "yaw": yaw}}
                ]

                delta = {
                    "context": "vessels.self",
                    "updates": [{
                        "source": {"label": "pi-sensehat"},
                        "timestamp": datetime_iso(),
                        "values": updates
                    }]
                }
                headers = {"Authorization": f"Bearer {SIGNALK_TOKEN}"}
                requests.post(SIGNALK_URL, json=delta, headers=headers, timeout=0.5)

            except Exception as e:
                pass
        
        time.sleep(1.0) 

# --- Web Server ---
class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_ROOT, **kwargs)

    def do_GET(self):
        if self.path.startswith("/face/"):
            face = self.path.split("/")[2]
            set_face(face)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"face": face, "status": "ok"}).encode())
            return
        
        if self.path == "/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            stat = {"face": current_face, "sensors": "active" if sense else "emulation"}
            if sense:
                try:
                    stat["temp"] = round(sense.get_temperature(), 1)
                    stat["pressure"] = round(sense.get_pressure(), 1)
                except Exception as e:
                    stat["error"] = str(e)
                    
            self.wfile.write(json.dumps(stat).encode())
            return

        super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/sensors":
            # Just verify auth/forwarding presence
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                headers = {"Authorization": f"Bearer {SIGNALK_TOKEN}", "Content-Type": "application/json"}
                requests.post(SIGNALK_URL, json=data, headers=headers, timeout=1.0)
                
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b"OK")
            except Exception as e:
                print(f"Proxy Error: {e}")
                self.send_response(500)
                self.end_headers()
            return
            
        self.send_response(404)
        self.end_headers()

def run_server():
    print(f"Starting Web Server on port {PORT}...")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), RequestHandler)
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=sensor_loop)
    t.daemon = True
    t.start()

    # Start Signal K WebSocket connection
    t_ws = threading.Thread(target=connect_signalk_ws)
    t_ws.daemon = True
    t_ws.start()

    run_mqtt() # Start MQTT Client

    set_face("neutral")

    try:
        run_server()
    except KeyboardInterrupt:
        stop_event.set()
        print("\nStopping...")
