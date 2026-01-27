# Hardware Plan (Current)

Version: 1.1 (draft)
Last updated: 2026-01-25

This is a working plan, not final. It captures the current hardware split and wiring intent.

## Roles and responsibilities

Jetson Orin Nano (backend, headless):
- AI processing, sensor fusion, storage
- Serves REST + WebSocket to the UI

Raspberry Pi 4 (frontend + bridge):
- Touchscreen dashboard UI
- Reads Arduino via USB serial
- Reads Sense HAT via I2C for environmental + IMU sensors
- Controls sensor power and outputs for maintenance

Arduino UNO + Grove Base Shield v2 (sensor hub):
- Analog and digital sensors
- I2C sensors via Grove ports

Raspberry Pi Sense HAT (sensor HAT):
- Environmental sensors (temperature, humidity, pressure)
- IMU (accelerometer, gyroscope, magnetometer)
GPIO extension cable (expansion):
- Pass-through wiring only (no additional ICs)

## Communication links

Arduino -> Raspberry Pi:
- USB serial
- Device: /dev/ttyACM0
- Baud: 115200

Raspberry Pi -> Jetson:
- Ethernet preferred (or USB-C)
- REST + WebSocket

## Sensor map (draft)

Analog ports (A0-A3):
- A0 flame_sensor (fire risk)
- A1 sound_level (microphone)
- A2 pulse_sensor (heart rate)
- A3 vibration (piezo)

Digital ports (D2-D8):
- D2 ultrasonic_cm
- D3 tilt (0 ok, 1 tilt)
- D4 hit (0 ok, 1 impact)
- D5 obstacle (0 clear, 1 obstacle)
- D6 touch_button (operator input)
- D7 buzzer (output, controlled by Pi)
- D8 relay (output, controlled by Pi)

I2C ports:
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

## Power and maintenance

- Jetson: DC jack 9-19V, dedicated supply
- Raspberry Pi: USB-C 5.1V 3A+ (touchscreen load)
- Arduino: powered from Raspberry Pi USB
- Pi controls D7/D8 so sensors/outputs can be disabled during maintenance without shutting down the full system

## Pinout summary

Raspberry Pi 4 J8 (3.3V logic):
- UART: TXD0=Pin 8 (GPIO14), RXD0=Pin 10 (GPIO15)
- I2C: SDA1=Pin 3 (GPIO2), SCL1=Pin 5 (GPIO3)

Jetson Orin Nano carrier J12 (3.3V level shifted):
- UART: TX=Pin 8, RX=Pin 10
- I2C_2: SDA=Pin 3, SCL=Pin 5

Arduino UNO (5V logic):
- UART: TX=D1, RX=D0
- I2C: SDA=A4, SCL=A5
