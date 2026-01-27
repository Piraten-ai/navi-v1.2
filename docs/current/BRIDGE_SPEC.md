# Arduino Bridge Spec (Current)

This spec defines the Arduino -> Raspberry Pi -> Jetson data path, plus Sense HAT telemetry.

## Input format (Arduino to Pi)

One JSON object per line over serial:

```
{"timestamp":"2026-01-25T12:00:00Z","signals":{"rpm":1200,"temp_c":62.1}}
```

## Link details (from hardware list)

Arduino -> Raspberry Pi:
- Transport: USB serial
- Device: /dev/ttyACM0
- Baud: 115200

Raspberry Pi -> Jetson:
- Transport: Ethernet (preferred) or USB-C
- Protocol: REST + WebSocket

## Transport (Pi to Jetson)

HTTP POST from the bridge service to Jetson:

```
POST /api/v1/bridge/analog
Content-Type: application/json
```

Payload is the same JSON object received from serial.

Sense HAT telemetry is emitted by the bridge service with `source: "sense_hat"` and the
signals listed below.

## Endpoint behavior

- POST /api/v1/bridge/analog accepts the payload and broadcasts it on WebSocket as:
  - type: "bridge"
  - data.signals: object
  - data.source: string
  - timestamp: ISO-8601
- GET /api/v1/bridge/analog returns the latest payload or {"status":"empty"}.

## Signal map (initial)

- rpm (int)
- temp_c (float)
- voltage_v (float)
- current_a (float)
- fuel_pct (float)

## Sensor map draft (from hardware list)

Analog (Arduino A0-A3 via Grove Base Shield v2):
- A0 flame_sensor (fire risk, analog)
- A1 sound_level (microphone, analog)
- A2 pulse_sensor (heart rate, analog)
- A3 vibration (piezo, analog)

Digital (Arduino D2-D8 via Grove Base Shield v2):
- D2 ultrasonic_cm (distance, digital)
- D3 tilt (0 ok, 1 tilt)
- D4 hit (0 ok, 1 impact)
- D5 obstacle (0 clear, 1 obstacle)
- D6 touch_button (operator input)
- D7 buzzer (output)
- D8 relay (output)

I2C (Arduino I2C ports):
- temp_humidity (c, percent)
- accel_xyz (x,y,z)

Sense HAT (Raspberry Pi I2C):
- sense_temp_c
- sense_humidity_pct
- sense_pressure_hpa
- sense_pitch_deg
- sense_roll_deg
- sense_yaw_deg
- sense_accel_x, sense_accel_y, sense_accel_z
- sense_gyro_x, sense_gyro_y, sense_gyro_z
- sense_mag_x, sense_mag_y, sense_mag_z

## Output control

D7 (buzzer) and D8 (relay) should be controlled by the Raspberry Pi so sensors can be disabled for maintenance without shutting down the full system.

## Multiple sources

If a second serial device is present, configure `SERIAL_DEVICE_2` to ingest it. It will publish with `source: "arduino_2"`.

## Hardware pinouts (from hardware manuals)

Raspberry Pi 4 J8 (3.3V logic, not 5V tolerant):
- UART: TXD0=Pin 8 (GPIO14), RXD0=Pin 10 (GPIO15)
- I2C: SDA1=Pin 3 (GPIO2), SCL1=Pin 5 (GPIO3)
- Power: 3.3V=Pin 1/17, 5V=Pin 2/4, GND=Pin 6/9/14/20/25/30/34/39

Jetson Orin Nano carrier J12 (3.3V level shifted):
- UART: TX=Pin 8, RX=Pin 10
- I2C_2: SDA=Pin 3, SCL=Pin 5
- Power: 3.3V=Pin 1/17, 5V=Pin 2/4, GND=Pin 6/9/14/20/25/30/34/39

Arduino UNO R3 (5V logic):
- UART: TX=D1, RX=D0
- I2C: SDA=A4, SCL=A5
- Analog: A0-A5 (0-5V)
- Power: 5V, 3.3V (50mA max), GND, VIN (6-20V)

Seed Base Shield v2:
- Switchable 3.3V/5V for Grove ports
- Analog Grove ports A0-A3, Digital D2-D8, UART and I2C ports

## Backend status

The Jetson backend implements `/api/v1/bridge/analog` for ingest and broadcast.

## Persistence

When InfluxDB is configured, the backend logs signals to measurement `bridge_analog`
with tag `source` and fields for each signal name.
