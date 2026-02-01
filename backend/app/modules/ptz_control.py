"""PTZ (Pan/Tilt/Zoom) Control Module for IP Camera

Controls ONVIF-compatible IP cameras (tested with EZVIZ).
Supports continuous pan/tilt/zoom and absolute positioning.
"""

import asyncio
import logging
from typing import Optional, Callable, Awaitable, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PTZPosition:
    """Camera position"""
    pan_deg: float = 0.0  # -180 to 180
    tilt_deg: float = 0.0  # -90 to 90
    zoom: float = 0.0  # 0.0 to 1.0


class PTZController:
    """Manages Pan/Tilt/Zoom for ONVIF cameras"""

    def __init__(
        self,
        camera_ip: str,
        camera_port: int = 8000,
        username: str = "admin",
        password: str = "admin",
    ):
        self.camera_ip = camera_ip
        self.camera_port = camera_port
        self.username = username
        self.password = password

        self.onvif_camera = None
        self.ptz_service = None
        self.profile_token = None
        self.current_position = PTZPosition()
        self.connected = False
        self._broadcast: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None

    def set_broadcast(self, broadcast: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Set callback for broadcasting status updates"""
        self._broadcast = broadcast

    async def connect(self) -> bool:
        """Connect to ONVIF camera"""
        try:
            from onvif import ONVIFCamera

            logger.info(f"Connecting to ONVIF camera at {self.camera_ip}:{self.camera_port}...")

            self.onvif_camera = ONVIFCamera(
                self.camera_ip,
                self.camera_port,
                self.username,
                self.password,
            )

            # Get media service and profiles
            media = self.onvif_camera.create_media_service()
            profiles = media.GetProfiles()

            if not profiles:
                raise Exception("No media profiles found")

            self.profile_token = profiles[0].token

            # Create PTZ service
            self.ptz_service = self.onvif_camera.create_ptz_service()

            self.connected = True
            logger.info(f"Connected to camera. Profile token: {self.profile_token}")
            await self._broadcast_status()
            return True

        except Exception as e:
            logger.error(f"Failed to connect to ONVIF camera: {e}")
            self.connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from camera"""
        try:
            if self.ptz_service:
                # Stop any ongoing movement
                req = self.ptz_service.create_type('Stop')
                req.ProfileToken = self.profile_token
                req.PanTilt = True
                req.Zoom = True
                self.ptz_service.Stop(req)
            self.connected = False
            logger.info("Disconnected from camera")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")

    async def pan_tilt_continuous(
        self,
        pan_speed: float,  # -1.0 to 1.0 (negative = left, positive = right)
        tilt_speed: float,  # -1.0 to 1.0 (negative = down, positive = up)
        duration_sec: float = 1.0,
    ) -> bool:
        """Move camera continuously"""
        if not self.connected or not self.ptz_service:
            logger.warning("Camera not connected")
            return False

        try:
            # Clamp speeds to valid range
            pan_speed = max(-1.0, min(1.0, pan_speed))
            tilt_speed = max(-1.0, min(1.0, tilt_speed))

            # Create continuous move request
            req = self.ptz_service.create_type('ContinuousMove')
            req.ProfileToken = self.profile_token
            req.Velocity = {
                'PanTilt': {
                    'x': pan_speed,
                    'y': tilt_speed,
                }
            }

            # Start movement
            self.ptz_service.ContinuousMove(req)

            # Wait for duration
            await asyncio.sleep(duration_sec)

            # Stop movement
            stop_req = self.ptz_service.create_type('Stop')
            stop_req.ProfileToken = self.profile_token
            stop_req.PanTilt = True
            stop_req.Zoom = False
            self.ptz_service.Stop(stop_req)

            logger.debug(f"Pan/Tilt continuous: pan={pan_speed}, tilt={tilt_speed}, duration={duration_sec}s")
            await self._broadcast_status()
            return True

        except Exception as e:
            logger.error(f"Error in continuous pan/tilt: {e}")
            return False

    async def pan_left(self, speed: float = 0.5, duration_sec: float = 1.0) -> bool:
        """Pan camera left"""
        return await self.pan_tilt_continuous(-abs(speed), 0, duration_sec)

    async def pan_right(self, speed: float = 0.5, duration_sec: float = 1.0) -> bool:
        """Pan camera right"""
        return await self.pan_tilt_continuous(abs(speed), 0, duration_sec)

    async def tilt_up(self, speed: float = 0.5, duration_sec: float = 1.0) -> bool:
        """Tilt camera up"""
        return await self.pan_tilt_continuous(0, abs(speed), duration_sec)

    async def tilt_down(self, speed: float = 0.5, duration_sec: float = 1.0) -> bool:
        """Tilt camera down"""
        return await self.pan_tilt_continuous(0, -abs(speed), duration_sec)

    async def absolute_move(
        self,
        pan_deg: float,  # -180 to 180
        tilt_deg: float,  # -90 to 90
        zoom: float = 0.0,  # 0.0 to 1.0
    ) -> bool:
        """Move to absolute position"""
        if not self.connected or not self.ptz_service:
            logger.warning("Camera not connected")
            return False

        try:
            # Clamp values to valid ranges
            pan_deg = max(-180.0, min(180.0, pan_deg))
            tilt_deg = max(-90.0, min(90.0, tilt_deg))
            zoom = max(0.0, min(1.0, zoom))

            # Create absolute move request
            req = self.ptz_service.create_type('AbsoluteMove')
            req.ProfileToken = self.profile_token
            req.Position = {
                'PanTilt': {
                    'x': pan_deg / 180.0,  # Normalize to -1.0 to 1.0
                    'y': tilt_deg / 90.0,  # Normalize to -1.0 to 1.0
                },
                'Zoom': {'x': zoom},
            }

            # Execute move
            self.ptz_service.AbsoluteMove(req)

            # Update current position
            self.current_position = PTZPosition(
                pan_deg=pan_deg,
                tilt_deg=tilt_deg,
                zoom=zoom,
            )

            logger.info(f"Absolute move: pan={pan_deg}°, tilt={tilt_deg}°, zoom={zoom}")
            await self._broadcast_status()
            return True

        except Exception as e:
            logger.error(f"Error in absolute move: {e}")
            return False

    async def home(self) -> bool:
        """Move to home position (center)"""
        return await self.absolute_move(0.0, 0.0, 0.0)

    async def auto_scan(
        self,
        duration_sec: float = 10.0,
        pan_speed: float = 0.3,
        scan_type: str = "sweep",  # sweep, circle, figure8
    ) -> None:
        """Run automated scanning pattern"""
        if not self.connected:
            logger.warning("Camera not connected")
            return

        try:
            logger.info(f"Starting auto-scan ({scan_type}) for {duration_sec}s")
            start_time = asyncio.get_event_loop().time()

            if scan_type == "sweep":
                # Sweep left-right continuously
                while asyncio.get_event_loop().time() - start_time < duration_sec:
                    await self.pan_left(pan_speed, 2.0)
                    await self.pan_right(pan_speed, 2.0)

            elif scan_type == "circle":
                # Circular pattern
                while asyncio.get_event_loop().time() - start_time < duration_sec:
                    for angle in range(0, 360, 45):
                        if asyncio.get_event_loop().time() - start_time >= duration_sec:
                            break
                        pan = (angle - 180) * 180 / 360
                        tilt = 30 * ((angle % 180) / 180)
                        await self.absolute_move(pan, tilt)
                        await asyncio.sleep(0.5)

            elif scan_type == "figure8":
                # Figure-8 pattern
                while asyncio.get_event_loop().time() - start_time < duration_sec:
                    for t in [i / 20 for i in range(40)]:
                        if asyncio.get_event_loop().time() - start_time >= duration_sec:
                            break
                        import math
                        pan = 90 * math.sin(2 * math.pi * t)
                        tilt = 45 * math.sin(4 * math.pi * t)
                        await self.absolute_move(pan, tilt)
                        await asyncio.sleep(0.1)

            logger.info("Auto-scan completed")
            await self.home()

        except Exception as e:
            logger.error(f"Error in auto-scan: {e}")

    async def track_object(
        self,
        bbox: tuple,  # (x1, y1, x2, y2) in normalized frame coords
        frame_width: int = 1920,
        frame_height: int = 1080,
    ) -> bool:
        """Track detected object by adjusting camera"""
        if not self.connected:
            return False

        try:
            # Calculate object center in frame
            x1, y1, x2, y2 = bbox
            obj_center_x = (x1 + x2) / 2.0 / frame_width  # Normalize 0-1
            obj_center_y = (y1 + y2) / 2.0 / frame_height

            # Frame center is 0.5, 0.5
            # Calculate offset and convert to pan/tilt adjustment
            pan_offset = (obj_center_x - 0.5) * 60.0  # ±30° for ±0.5 offset
            tilt_offset = -(obj_center_y - 0.5) * 45.0  # ±22.5° (inverted Y)

            # Move camera to center on object
            new_pan = self.current_position.pan_deg + pan_offset * 0.1  # Smooth adjustment
            new_tilt = self.current_position.tilt_deg + tilt_offset * 0.1

            return await self.absolute_move(new_pan, new_tilt)

        except Exception as e:
            logger.error(f"Error in object tracking: {e}")
            return False

    async def get_status(self) -> Dict[str, Any]:
        """Get current camera status"""
        return {
            "connected": self.connected,
            "camera_ip": self.camera_ip,
            "position": {
                "pan_deg": self.current_position.pan_deg,
                "tilt_deg": self.current_position.tilt_deg,
                "zoom": self.current_position.zoom,
            },
        }

    async def _broadcast_status(self) -> None:
        """Broadcast status update to all connected clients"""
        if self._broadcast:
            try:
                await self._broadcast({
                    "type": "ptz_status",
                    "data": await self.get_status(),
                })
            except Exception as e:
                logger.error(f"Error broadcasting PTZ status: {e}")
