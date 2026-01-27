# Offline Tileserver (MBTiles)

This UI expects a local tileserver that serves MBTiles over HTTP. The default
URL in Settings is:

```
http://localhost:8080/styles/raster/
```

That matches `tileserver-gl` when serving raster MBTiles.

## Docker (recommended)

1) Place your `.mbtiles` file on the Pi, for example:

```
/opt/aads/tiles/openseamap.mbtiles
```

2) Start the tileserver container (compose):

```
docker compose -f /opt/aads/frontend-qt/tileserver/docker-compose.tiles.yml up -d
```

3) Confirm the tileserver is serving:

```
http://localhost:8080/styles/
```

4) Set the UI tile URL to:

```
http://localhost:8080/styles/raster/
```

If your MBTiles is vector, use the style name shown in `/styles/`.

## Systemd for tileserver

```
sudo cp /opt/aads/frontend-qt/tileserver/aads-tileserver.service /etc/systemd/system/aads-tileserver.service
sudo systemctl daemon-reload
sudo systemctl enable --now aads-tileserver.service
```

## KAP to MBTiles (offline conversion)

If you have KAP charts, convert them to MBTiles once, then serve them locally.

Recommended default paths on the Pi:

```
/opt/aads/charts/kap
/opt/aads/tiles
```

Example (GDAL):

```
sudo apt install -y gdal-bin
mkdir -p /opt/aads/charts/kap /opt/aads/tiles
gdal_translate -of MBTILES /opt/aads/charts/kap/chart.kap /opt/aads/tiles/chart.mbtiles
```

Then point the tileserver at `/opt/aads/tiles`.

## Systemd (optional)

Create a systemd unit to keep the tileserver running if you prefer not to use
Docker. Any HTTP server that exposes `{z}/{x}/{y}.png` or a tileserver-gl
`/styles/<style>/` endpoint works.
