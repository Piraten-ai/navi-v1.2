#!/usr/bin/env bash
set -euo pipefail

# Simulate Arduino -> Pi serial feed using socat.
# This creates a virtual pair and prints sample JSON lines into one end.

if ! command -v socat >/dev/null 2>&1; then
  echo "socat is required. Install with: sudo apt-get install -y socat"
  exit 1
fi

VPORT_A=${1:-/tmp/ttyV0}
VPORT_B=${2:-/tmp/ttyV1}

echo "Creating virtual serial pair: $VPORT_A <-> $VPORT_B"
socat -d -d pty,raw,echo=0,link="$VPORT_A" pty,raw,echo=0,link="$VPORT_B" &
SOCAT_PID=$!

cleanup() {
  kill "$SOCAT_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "Point the bridge to SERIAL_DEVICE=$VPORT_A"
echo "Sending sample payloads to $VPORT_B"

while true; do
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "{\"timestamp\":\"$ts\",\"signals\":{\"rpm\":$((RANDOM % 2000 + 800)),\"temp_c\":$((RANDOM % 30 + 40)).$((RANDOM % 9)),\"vibration\":$((RANDOM % 100))}}" > "$VPORT_B"
  sleep 1
done
