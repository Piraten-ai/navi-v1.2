#!/usr/bin/env python3
import os
import subprocess
import time


def _get_env(path, key, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == key:
                return v.strip()
    return default


def _systemctl(action, unit):
    return subprocess.run(["/usr/bin/systemctl", action, unit], check=False, capture_output=True, text=True)


def main():
    env_path = "/etc/aads-kiosk-unlock.env"
    pin = int(_get_env(env_path, "AADS_UNLOCK_GPIO", "17"))
    hold_seconds = float(_get_env(env_path, "AADS_UNLOCK_HOLD", "2.5"))
    unit = _get_env(env_path, "AADS_UI_SERVICE", "aads-ui.service")

    try:
        from gpiozero import Button
    except ImportError as exc:
        raise SystemExit("gpiozero not installed. Install with: sudo apt install -y python3-gpiozero") from exc

    button = Button(pin, pull_up=True, hold_time=hold_seconds, bounce_time=0.05)

    def on_hold():
        # Toggle kiosk UI service on long press.
        status = _systemctl("is-active", unit)
        if status.returncode == 0 and status.stdout.strip() == "active":
            _systemctl("stop", unit)
        else:
            _systemctl("start", unit)

    button.when_held = on_hold

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
