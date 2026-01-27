# backend/app/modules/voice_system.py
"""
NAVI Voice System – Piper TTS + Whisper STT
Offline-first voice interface with Zelda "Hey Listen" alerts
Jetson Orin Nano optimized (low latency, graceful fallback)
"""

import asyncio
import io
import os
import wave
from typing import Optional, Callable
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Optional dependencies with graceful fallback
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger.warning("pygame not available – audio playback disabled")

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except (ImportError, OSError) as e:
    SOUNDDEVICE_AVAILABLE = False
    logger.warning(f"sounddevice not available ({type(e).__name__}: {e}) – microphone recording disabled")

try:
    import whisper
    WHISPER_AVAILABLE = True
    whisper_model = None  # Lazy loaded
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("openai-whisper not available – STT disabled")

try:
    from piper.voice import PiperVoice
    PIPER_AVAILABLE = True
    piper_voice = None  # Lazy loaded
except ImportError:
    PIPER_AVAILABLE = False
    logger.warning("piper-tts not available – TTS disabled")

# Navi alert sound path
NAVI_ALERT_MP3 = "/app/audio/hey_listen.mp3"

# TTS Parameters – Navi-like (high pitch, fast, energetic)
TTS_CONFIG = {
    "pitch_scale": 1.3,  # Higher pitch for Navi feel
    "speaking_rate": 1.25,  # Faster delivery
    "length_scale": 0.95,  # Slightly compressed
    "noise_scale": 0.667,  # Natural variation
    "noise_w": 0.8,
}


def initialize_voice_system() -> None:
    """Initialize voice system components (lazy loading)"""
    global piper_voice, whisper_model

    if PIPER_AVAILABLE and piper_voice is None:
        try:
            voice_model_path = getattr(settings, 'PIPER_VOICE_MODEL', '/app/models/piper/en_US-lessac-medium.onnx')
            if os.path.exists(voice_model_path):
                piper_voice = PiperVoice.load(voice_model_path)
                logger.info(f"Piper voice loaded: {voice_model_path}")
            else:
                logger.warning(f"Piper model not found: {voice_model_path}")
        except Exception as e:
            logger.error(f"Failed to load Piper voice: {e}")

    if WHISPER_AVAILABLE and whisper_model is None:
        try:
            model_size = getattr(settings, 'WHISPER_MODEL_SIZE', 'tiny.en')
            whisper_model = whisper.load_model(model_size)
            logger.info(f"Whisper model loaded: {model_size}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")

    if PYGAME_AVAILABLE:
        try:
            pygame.mixer.init()
            logger.info("pygame mixer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize pygame: {e}")


async def play_voice_alert(message: str, is_critical: bool = False) -> None:
    """
    Play voice alert with optional "Hey Listen!" prefix for critical alerts
    
    Args:
        message: Alert text to synthesize
        is_critical: If True, play Zelda "Hey Listen!" MP3 first
    """
    if not PIPER_AVAILABLE or piper_voice is None:
        logger.warning("Piper TTS not available – skipping voice alert")
        return

    try:
        # Critical alerts start with Zelda "Hey Listen!"
        if is_critical and PYGAME_AVAILABLE and os.path.exists(NAVI_ALERT_MP3):
            try:
                pygame.mixer.Sound(NAVI_ALERT_MP3).play()
                await asyncio.sleep(1.5)  # Wait for sound
            except Exception as e:
                logger.error(f"Failed to play alert sound: {e}")

        # TTS the message with Navi tuning
        wav_bytes = piper_voice.synthesize(message, **TTS_CONFIG)
        wav_path = '/tmp/tts_alert.wav'

        with wave.open(wav_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(22050)
            wav_file.writeframes(wav_bytes)

        if PYGAME_AVAILABLE:
            pygame.mixer.Sound(wav_path).play()
            logger.info(f"Voice alert played: {message}")
        else:
            logger.info(f"Voice alert text (audio output disabled): {message}")

    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")


async def speak_response(text: str) -> Optional[bytes]:
    """
    Synthesize text-to-speech response
    
    Args:
        text: Response text to synthesize
        
    Returns:
        WAV audio bytes if successful, None otherwise
    """
    if not PIPER_AVAILABLE or piper_voice is None:
        logger.warning("Piper TTS not available – skipping voice response")
        return None

    try:
        wav_bytes = piper_voice.synthesize(text, **TTS_CONFIG)
        wav_path = '/tmp/tts_response.wav'

        with wave.open(wav_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(22050)
            wav_file.writeframes(wav_bytes)

        if PYGAME_AVAILABLE:
            pygame.mixer.Sound(wav_path).play()
            logger.info(f"Voice response played: {text}")

        return wav_bytes
    except Exception as e:
        logger.error(f"TTS response error: {e}")
        return None


async def process_voice_input(audio_data: np.ndarray, state_provider: Optional[Callable] = None) -> Optional[str]:
    """
    Process voice input (STT) and return command text
    
    Args:
        audio_data: Audio samples as numpy array (mono, float or int16)
        state_provider: Optional callable to get current system state for context-aware responses
        
    Returns:
        Recognized command text, or None if STT failed
    """
    if not WHISPER_AVAILABLE or whisper_model is None:
        logger.warning("Whisper STT not available – skipping voice input processing")
        return None

    try:
        # Convert to float32 if needed
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32) / 32768.0

        # Transcribe
        result = whisper_model.transcribe(audio_data, fp16=False, verbose=False)
        command = result.get("text", "").strip().lower()

        if not command:
            logger.warning("Empty command from STT")
            return None

        logger.info(f"Voice command received: {command}")

        # Generate response based on command
        response = await generate_voice_response(command, state_provider)
        if response:
            await speak_response(response)

        return command
    except Exception as e:
        logger.error(f"STT processing error: {e}")
        return None


async def generate_voice_response(
    command: str, state_provider: Optional[Callable] = None
) -> Optional[str]:
    """
    Generate a voice response to a recognized command
    
    Args:
        command: Recognized command text (lowercase)
        state_provider: Optional callable returning dict of system state
        
    Returns:
        Response text to speak, or None
    """
    # Command patterns
    if "status" in command or "navi" in command or "hey navi" in command:
        return "All systems nominal. Ready for your command."

    if "alerts" in command or "warning" in command:
        return "No critical alerts at this time."

    if "autopilot" in command or "heading" in command:
        state = state_provider() if state_provider else {}
        heading = state.get('desired_heading_deg', '---')
        return f"Autopilot on heading {heading} degrees."

    if "wind" in command:
        state = state_provider() if state_provider else {}
        ws = state.get('apparent_wind_speed', '---')
        wd = state.get('apparent_wind_angle', '---')
        return f"Wind {ws} knots from {wd} degrees."

    if "position" in command or "gps" in command:
        state = state_provider() if state_provider else {}
        lat = state.get('latitude', '---')
        lon = state.get('longitude', '---')
        return f"Position {lat} by {lon}."

    if "help" in command or "commands" in command:
        return "Try: status, alerts, autopilot, wind, position, or help."

    return "Command not recognized. Try 'status' or 'help'."


async def record_microphone(duration_seconds: float = 5.0) -> Optional[np.ndarray]:
    """
    Record audio from microphone
    
    Args:
        duration_seconds: Duration to record in seconds
        
    Returns:
        Audio samples as numpy array, or None if recording failed
    """
    if not SOUNDDEVICE_AVAILABLE:
        logger.warning("sounddevice not available – cannot record microphone")
        return None

    try:
        logger.info(f"Recording for {duration_seconds}s...")
        audio = sd.rec(int(duration_seconds * 22050), samplerate=22050, channels=1)
        sd.wait()
        logger.info("Recording complete")
        return audio.flatten()
    except Exception as e:
        logger.error(f"Microphone recording error: {e}")
        return None


# Singleton instance for voice system
class VoiceSystem:
    """Voice system manager (Piper TTS + Whisper STT)"""

    def __init__(self):
        self.initialized = False
        self.state_provider: Optional[Callable] = None

    async def initialize(self, state_provider: Optional[Callable] = None) -> None:
        """Initialize voice system with optional state provider"""
        initialize_voice_system()
        self.state_provider = state_provider
        self.initialized = True
        logger.info("Voice system initialized")

    async def alert(self, message: str, is_critical: bool = False) -> None:
        """Play alert message"""
        if not self.initialized:
            return
        await play_voice_alert(message, is_critical)

    async def respond(self, text: str) -> Optional[bytes]:
        """Generate voice response"""
        if not self.initialized:
            return None
        return await speak_response(text)

    async def process_audio(self, audio_data: np.ndarray) -> Optional[str]:
        """Process audio input (STT)"""
        if not self.initialized:
            return None
        return await process_voice_input(audio_data, self.state_provider)

    async def record(self, duration_seconds: float = 5.0) -> Optional[np.ndarray]:
        """Record from microphone"""
        return await record_microphone(duration_seconds)


# Global instance
voice_system = VoiceSystem()
