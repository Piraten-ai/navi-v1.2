"""
Stable Diffusion ML module for image generation
Supports: map visualization, weather rendering, safety alerts, training data
"""

import asyncio
import os
from typing import Optional
import logging
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)


class StableDiffusionModule:
    """Generative image ML module using Stable Diffusion"""

    def __init__(self, sd_api_url: str = "http://sd-api:5000", mock_mode: bool = False):
        self.sd_api_url = sd_api_url
        self.mock_mode = mock_mode
        self.session = None
        self.initialized = False

    async def initialize(self):
        """Initialize connection to Stable Diffusion API"""
        if self.initialized:
            return
        
        try:
            self.session = aiohttp.ClientSession()
            # Test connection
            async with self.session.get(f"{self.sd_api_url}/health") as resp:
                if resp.status == 200:
                    self.initialized = True
                    logger.info("✓ Stable Diffusion API connected")
                else:
                    logger.warning(f"SD API health check failed: {resp.status}")
        except Exception as e:
            logger.error(f"Failed to initialize SD module: {e}")
            self.initialized = False

    async def generate_map_visualization(
        self,
        location: str,
        route_description: str,
        hazards: Optional[list] = None,
        width: int = 768,
        height: int = 768
    ) -> str:
        """Generate maritime map visualization"""
        if self.mock_mode:
            return "/mock/map.png"

        prompt = f"Professional nautical chart visualization of {location}. "
        prompt += f"Route: {route_description}. "
        if hazards:
            prompt += f"Show hazards: {', '.join(hazards)}. "
        prompt += "Nautical style, accurate, professional, maritime theme."

        return await self._generate_image(prompt, width, height, "map")

    async def generate_weather_visualization(
        self,
        conditions: dict,
        location: str,
        width: int = 512,
        height: int = 512
    ) -> str:
        """Generate weather visualization (storms, wind patterns, etc.)"""
        if self.mock_mode:
            return "/mock/weather.png"

        wind_speed = conditions.get("wind_speed", "unknown")
        wave_height = conditions.get("wave_height", "unknown")
        visibility = conditions.get("visibility", "unknown")

        prompt = f"Weather visualization for {location}: "
        prompt += f"Wind {wind_speed} knots, Waves {wave_height}m, Visibility {visibility}. "
        prompt += "Realistic weather, atmospheric, maritime conditions, professional."

        return await self._generate_image(prompt, width, height, "weather")

    async def generate_safety_alert_image(
        self,
        alert_type: str,
        severity: str,
        description: str,
        width: int = 512,
        height: int = 512
    ) -> str:
        """Generate warning/alert visualization"""
        if self.mock_mode:
            return "/mock/alert.png"

        severity_colors = {
            "critical": "red emergency flashing",
            "high": "orange warning",
            "medium": "yellow caution",
            "low": "blue info"
        }

        color_desc = severity_colors.get(severity.lower(), "warning")
        prompt = f"{color_desc} alert visualization for {alert_type}. "
        prompt += f"Issue: {description}. "
        prompt += "Clear, professional safety graphic, urgent, maritime context."

        return await self._generate_image(prompt, width, height, "alert")

    async def generate_training_data(
        self,
        scenario: str,
        variations: int = 5,
        width: int = 512,
        height: int = 512
    ) -> list:
        """Generate synthetic training data for ML models"""
        if self.mock_mode:
            return [f"/mock/training_{i}.png" for i in range(variations)]

        images = []
        prompts = [
            f"{scenario} - variation {i+1}, diverse angle, realistic maritime setting"
            for i in range(variations)
        ]

        for prompt in prompts:
            img_path = await self._generate_image(prompt, width, height, "training")
            images.append(img_path)

        return images

    async def _generate_image(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        image_type: str = "general"
    ) -> str:
        """Internal method to generate image via SD API"""
        if not self.initialized and not self.mock_mode:
            await self.initialize()

        if not self.initialized and not self.mock_mode:
            logger.warning("SD API not initialized, returning mock path")
            return f"/mock/{image_type}.png"

        try:
            payload = {
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, distorted",
                "width": width,
                "height": height,
                "steps": 20,
                "guidance_scale": 7.5,
                "seed": -1
            }

            async with self.session.post(
                f"{self.sd_api_url}/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    image_path = data.get("image_path", f"/images/{image_type}_{datetime.now().timestamp()}.png")
                    logger.info(f"Generated {image_type} image: {image_path}")
                    return image_path
                else:
                    logger.error(f"SD API error: {resp.status}")
                    return f"/mock/{image_type}.png"

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return f"/mock/{image_type}.png"

    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            self.initialized = False

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
