import json
import os
import sys
import time
from datetime import datetime, timezone
import threading

import requests
import serial

try:
    from sense_hat import SenseHat

    SENSE_HAT_AVAILABLE = True
except Exception:
    SenseHat = None
    SENSE_HAT_AVAILABLE = False


def get_env(name, default):
    value = os.getenv(name, default)
    return value if value is not None and value != "" else default


def get_env_bool(name, default):
    value = get_env(name, str(default)).strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default


def iso_now():
    return datetime.now(timezone.utc).isoformat()


def post_payload(session, url, payload):
    try:
        response = session.post(url, json=payload, timeout=2)
        if response.status_code >= 300:
            print(f"Bridge warning: HTTP {response.status_code} for payload source={payload.get('source')}")
    except requests.RequestException as exc:
        print(f"Bridge warning: request failed: {exc}")


def serial_reader_loop(label, ser, url):
    session = requests.Session()
    print(f"Bridge serial reader started: {label}")

    while True:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        if not line:
            time.sleep(0.05)
            continue

        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            print(f"Bridge warning: invalid JSON line ({label}): {line}")
            continue

        if isinstance(payload, dict) and "signals" in payload:
            message = payload
        elif isinstance(payload, dict):
            message = {"signals": payload}
        else:
            print(f"Bridge warning: unsupported payload from {label}: {payload}")
            continue

        if not message.get("timestamp"):
            message["timestamp"] = iso_now()
        if not message.get("source"):
            message["source"] = label

        post_payload(session, url, message)


def serial_heartbeat_loop(ser, interval_s=1.0):
    """Sends a heartbeat character to the Arduino to prevent failsafe lock-up."""
    print(f"Bridge heartbeat loop started (Interval: {interval_s}s)")
    while True:
        try:
            ser.write(b'H')
            ser.flush()
        except Exception as exc:
            print(f"Bridge warning: serial heartbeat failed: {exc}")
        time.sleep(interval_s)


def sense_hat_loop(url, interval_s):
    session = requests.Session()
    sense = SenseHat()
    print("Bridge Sense HAT reader started")

    while True:
        try:
            temp_h = sense.get_temperature_from_humidity()
            temp_p = sense.get_temperature_from_pressure()
            temp_c = (temp_h + temp_p) / 2.0
            humidity = sense.get_humidity()
            pressure = sense.get_pressure()
            orientation = sense.get_orientation()
            accel = sense.get_accelerometer_raw()
            gyro = sense.get_gyroscope_raw()
            compass = sense.get_compass_raw()

            payload = {
                "timestamp": iso_now(),
                "source": "sense_hat",
                "signals": {
                    "sense_temp_c": float(temp_c),
                    "sense_humidity_pct": float(humidity),
                    "sense_pressure_hpa": float(pressure),
                    "sense_pitch_deg": float(orientation.get("pitch", 0.0)),
                    "sense_roll_deg": float(orientation.get("roll", 0.0)),
                    "sense_yaw_deg": float(orientation.get("yaw", 0.0)),
                    "sense_accel_x": float(accel.get("x", 0.0)),
                    "sense_accel_y": float(accel.get("y", 0.0)),
                    "sense_accel_z": float(accel.get("z", 0.0)),
                    "sense_gyro_x": float(gyro.get("x", 0.0)),
                    "sense_gyro_y": float(gyro.get("y", 0.0)),
                    "sense_gyro_z": float(gyro.get("z", 0.0)),
                    "sense_mag_x": float(compass.get("x", 0.0)),
                    "sense_mag_y": float(compass.get("y", 0.0)),
                    "sense_mag_z": float(compass.get("z", 0.0)),
                },
            }
            post_payload(session, url, payload)
        except Exception as exc:
            print(f"Bridge warning: Sense HAT read failed: {exc}")

        time.sleep(interval_s)


def main():
    jetson_host = get_env("JETSON_HOST", "192.168.39.196")
    jetson_port = int(get_env("JETSON_PORT", "8000"))
    serial_device = get_env("SERIAL_DEVICE", "/dev/ttyACM0")
    serial_baud = int(get_env("SERIAL_BAUD", "115200"))
    serial_required = get_env_bool("SERIAL_REQUIRED", True)
    serial_enabled = get_env_bool("SERIAL_ENABLED", True)
    serial_device_2 = get_env("SERIAL_DEVICE_2", "")
    serial_baud_2 = int(get_env("SERIAL_BAUD_2", "115200"))
    endpoint = get_env("BRIDGE_ENDPOINT", "/api/v1/bridge/analog")
    sense_hat_enabled = get_env("SENSE_HAT_ENABLED", "auto").strip().lower()
    sense_hat_interval = float(get_env("SENSE_HAT_INTERVAL", "2.0"))

    url = f"http://{jetson_host}:{jetson_port}{endpoint}"

    print(f"Bridge started. URL={url}")

    threads = []

    if serial_enabled:
        try:
            ser = serial.Serial(serial_device, serial_baud, timeout=1)
        except Exception as exc:
            if serial_required:
                print(f"Bridge error: cannot open serial device: {exc}", file=sys.stderr)
                sys.exit(1)
            print(f"Bridge warning: serial disabled due to error: {exc}")
        else:
            print(f"Bridge serial enabled. Device={serial_device} Baud={serial_baud}")
            # Start reader
            reader_thread = threading.Thread(target=serial_reader_loop, args=("arduino", ser, url), daemon=True)
            reader_thread.start()
            threads.append(reader_thread)
            
            # Start Heartbeat sender (Crucial for failsafe)
            heartbeat_thread = threading.Thread(target=serial_heartbeat_loop, args=(ser,), daemon=True)
            heartbeat_thread.start()
            threads.append(heartbeat_thread)

    if serial_device_2:
        try:
            ser2 = serial.Serial(serial_device_2, serial_baud_2, timeout=1)
        except Exception as exc:
            print(f"Bridge warning: cannot open second serial device: {exc}")
        else:
            print(f"Bridge serial2 enabled. Device={serial_device_2} Baud={serial_baud_2}")
            thread = threading.Thread(target=serial_reader_loop, args=("arduino_2", ser2, url), daemon=True)
            thread.start()
            threads.append(thread)

    sense_hat_auto = sense_hat_enabled in {"auto", ""}
    sense_hat_on = sense_hat_enabled in {"1", "true", "yes", "on"}
    if (sense_hat_on or (sense_hat_auto and SENSE_HAT_AVAILABLE)) and not SENSE_HAT_AVAILABLE:
        print("Bridge warning: Sense HAT requested but sense_hat library unavailable")
    elif sense_hat_on or (sense_hat_auto and SENSE_HAT_AVAILABLE):
        thread = threading.Thread(target=sense_hat_loop, args=(url, sense_hat_interval), daemon=True)
        thread.start()
        threads.append(thread)
    else:
        print("Bridge Sense HAT disabled")

    if not threads:
        print("Bridge error: no data sources enabled", file=sys.stderr)
        sys.exit(1)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
