import asyncio
import json
import math
import os
import random
import threading
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen

import websockets


SIGNALK_WS_URL = os.getenv("SIGNALK_WS_URL", "ws://localhost:3001/signalk/v1/stream")
BRIDGE_URL = os.getenv("BRIDGE_URL", "http://localhost:8000/api/v1/bridge/analog")
SIM_INTERVAL = float(os.getenv("SIM_INTERVAL", "1.0"))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _send_bridge_payload() -> None:
    payload = {
        "timestamp": _now_iso(),
        "source": "simulator",
        "signals": {
            "battery_v": round(12.2 + random.uniform(-0.3, 0.3), 2),
            "engine_temp_c": round(65 + random.uniform(-2, 2), 1),
            "fuel_level_pct": round(72 + random.uniform(-1, 1), 1),
            "bilge": int(random.random() < 0.02),
            "rpm": int(900 + random.uniform(-50, 50)),
        },
    }

    data = json.dumps(payload).encode("utf-8")
    req = Request(
        BRIDGE_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=5) as resp:
        resp.read()


def _bridge_loop() -> None:
    while True:
        try:
            _send_bridge_payload()
        except Exception as exc:
            print(f"[bridge] error: {exc}")
        time.sleep(SIM_INTERVAL)


async def _signalk_loop() -> None:
    lat = 78.2232
    lon = 15.6469
    heading_deg = 45.0
    speed_ms = 4.0

    while True:
        try:
            async with websockets.connect(SIGNALK_WS_URL) as ws:
                print(f"[signalk] connected to {SIGNALK_WS_URL}")
                while True:
                    heading_deg = (heading_deg + random.uniform(-2, 2)) % 360
                    speed_ms = max(0.5, min(7.0, speed_ms + random.uniform(-0.2, 0.2)))

                    distance_m = speed_ms * SIM_INTERVAL
                    heading_rad = math.radians(heading_deg)
                    lat += (distance_m * math.cos(heading_rad)) / 111_111.0
                    lon += (distance_m * math.sin(heading_rad)) / (111_111.0 * math.cos(math.radians(lat)))

                    wind_speed = 6.0 + random.uniform(-1.0, 1.0)
                    wind_dir = (heading_deg + 120 + random.uniform(-10, 10)) % 360

                    delta = {
                        "context": "vessels.self",
                        "updates": [
                            {
                                "source": {"label": "simulator"},
                                "timestamp": _now_iso(),
                                "values": [
                                    {
                                        "path": "navigation.position",
                                        "value": {"latitude": lat, "longitude": lon},
                                    },
                                    {
                                        "path": "navigation.speedOverGround",
                                        "value": speed_ms,
                                    },
                                    {
                                        "path": "navigation.courseOverGroundTrue",
                                        "value": heading_rad,
                                    },
                                    {
                                        "path": "navigation.headingTrue",
                                        "value": heading_rad,
                                    },
                                    {
                                        "path": "environment.wind.speedTrue",
                                        "value": wind_speed,
                                    },
                                    {
                                        "path": "environment.wind.directionTrue",
                                        "value": math.radians(wind_dir),
                                    },
                                    {
                                        "path": "environment.depth.belowTransducer",
                                        "value": 42.0 + random.uniform(-1.0, 1.0),
                                    },
                                    {
                                        "path": "environment.water.temperature",
                                        "value": 273.15 + 2.0 + random.uniform(-0.2, 0.2),
                                    },
                                    {
                                        "path": "propulsion.main.revolutions",
                                        "value": 15.0 + random.uniform(-1.0, 1.0),
                                    },
                                    {
                                        "path": "tanks.fuel.0.currentLevel",
                                        "value": 0.72 + random.uniform(-0.01, 0.01),
                                    },
                                ],
                            }
                        ],
                    }

                    await ws.send(json.dumps(delta))
                    await asyncio.sleep(SIM_INTERVAL)
        except Exception as exc:
            print(f"[signalk] error: {exc}")
            await asyncio.sleep(2)


def main() -> None:
    bridge_thread = threading.Thread(target=_bridge_loop, daemon=True)
    bridge_thread.start()
    asyncio.run(_signalk_loop())


if __name__ == "__main__":
    main()
