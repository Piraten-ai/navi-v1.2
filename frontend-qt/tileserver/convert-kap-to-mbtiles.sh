#!/usr/bin/env bash
set -euo pipefail

KAP_DIR="/opt/aads/charts/kap"
OUT_DIR="/opt/aads/tiles"

if ! command -v gdal_translate >/dev/null 2>&1; then
  echo "gdal_translate not found. Install with: sudo apt install -y gdal-bin"
  exit 1
fi

mkdir -p "$KAP_DIR" "$OUT_DIR"

shopt -s nullglob
found=0
for kap in "$KAP_DIR"/*.kap "$KAP_DIR"/*.KAP; do
  found=1
  base="$(basename "$kap")"
  name="${base%.*}"
  out="$OUT_DIR/${name}.mbtiles"
  echo "Converting $kap -> $out"
  gdal_translate -of MBTILES "$kap" "$out"
done

if [ "$found" -eq 0 ]; then
  echo "No .kap files found in $KAP_DIR"
  exit 1
fi

echo "Done. MBTiles are in $OUT_DIR"
