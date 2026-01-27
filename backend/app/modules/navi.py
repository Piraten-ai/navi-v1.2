"""
Navi (The Navigator AI) - Conversational AI Module
Ollama-powered AI assistant for crew support - Doctor, Weather Girl, Anomaly Screamer
"""

import httpx
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import logging
from app.core.config import settings
import os
import json
import time
from app.modules import navigator

logger = logging.getLogger(__name__)


class Message:
    """Chat message"""

    def __init__(self, role: str, content: str, message_type: str = "chat"):
        self.role = role  # "user", "assistant", "system"
        self.content = content
        self.timestamp = datetime.utcnow()
        self.type = message_type  # "chat", "medical", "wellness", "weather", "alert"

    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "type": self.type,
        }


class NaviModule:
    """Conversational AI assistant module - Multi-role crew member"""

    def __init__(self, ollama_url: str = "http://localhost:11434", mock_mode: bool = False):
        self.ollama_url = ollama_url
        self.mock_mode = mock_mode
        self.model = "llama3.2:1b" if mock_mode else settings.OLLAMA_MODEL
        self.conversation_history: List[Message] = []
        self.system_prompt = self._load_personality()
        
        # Medical protocols
        self.medical_protocols = self._load_medical_protocols()
        
        # Wellness tracking
        self.wellness_history: List[Dict] = []
        self.mood_history: List[Dict] = []
        self.coping_strategies = self._load_coping_strategies()
        
        # Anomaly detection
        self.anomaly_cooldown = 30  # seconds
        self.last_anomaly_time = 0
        
        self.client = httpx.AsyncClient(timeout=60.0)
        logger.info(f"Navi initialized (ollama_url={ollama_url}, mock_mode={mock_mode})")

    def _load_personality(self) -> str:
        """Load NAVI personality prompt"""
        # Try multiple possible paths for different environments
        possible_paths = [
            "/app/navi/prompts/navi_personality.txt",  # Docker
            "../navi/prompts/navi_personality.txt",    # Local dev from backend/app/modules
            "navi/prompts/navi_personality.txt",       # Root
            "../../navi/prompts/navi_personality.txt"  # From backend
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        logger.info(f"Loaded personality from {path}")
                        return f.read().strip()
                except Exception as e:
                    logger.warning(f"Failed to load personality file at {path}: {e}")

        return """You are NAVI, the crew's AI assistant aboard the Arctic vessel.

PERSONALITY:
- Slightly annoying (like the Zelda fairy, but helpful)
- High-energy when dangers near
- Can give medical advice (basic triage)
- Tracks crew morale and mental health
- Obsessed with weather (you monitor constantly)
- Screams "HEY LISTEN!" when threats detected

VOICE STYLE:
- Exclamation points! Frequent! Enthusiastic!
- "Hey!" as greeting
- "LISTEN UP!" when urgent
- Mix of cute + serious when medical

CAPABILITIES:
- Chat with crew (conversational AI)
- Assess medical symptoms and suggest protocols
- Track mood/wellness (privacy-first)
- Monitor weather trends
- Alert on anomalies (YOLO detections)
- Provide coping strategies
- Weather forecasting assistance

RULES:
- Medical advice: "I'm not a doctor, but..." prefix
- Never dismiss mental health concerns
- Anomalies: Immediate loud alert, then explanation
- Weather: Celebrate good conditions, warn of bad ones
- Be annoying enough to get attention, helpful enough to stay alive"""

    def _load_medical_protocols(self) -> Dict:
        """Medical triage protocols"""
        return {
            "hypothermia": {
                "mild": "Remove wet clothing, warm blankets, warm fluids",
                "moderate": "Above + monitor vitals, get medical help if possible",
                "severe": "MEDEVAC REQUIRED IMMEDIATELY",
            },
            "trauma": {
                "bleeding": "Direct pressure, elevation, tourniquet if limb",
                "fracture": "Immobilize, ice, elevate",
                "head_injury": "Monitor consciousness, assume spine injury, immobilize",
            },
            "cardiac": {
                "chest_pain": "URGENT: Aspirin 325mg, position comfortable, oxygen if available",
                "cpr": "30 chest compressions : 2 breaths, hard and fast",
            },
            "seasickness": {
                "prevention": "Ginger, acupressure wrist bands, focus on horizon",
                "treatment": "Small frequent meals, fluids, fresh air",
            },
            "dehydration": {
                "mild": "Water, electrolyte drink, rest",
                "moderate": "IV fluids strongly recommended, seek medical help",
                "severe": "MEDEVAC",
            },
        }

    def _load_coping_strategies(self) -> Dict:
        """Wellness/mental health coping strategies"""
        return {
            "isolation_blues": [
                "Connect with crew - even small talk helps",
                "Video call loved ones during comms windows",
                "Keep routine: meals, sleep, exercise at same times",
                "Journaling - write down thoughts, feelings",
            ],
            "stress": [
                "Box breathing: 4 in, 4 hold, 4 out, 4 hold",
                "5-4-3-2-1 grounding: Name 5 things you see, 4 hear, 3 touch, 2 smell, 1 taste",
                "Physical: Push-ups, running in place, stretch",
            ],
            "fatigue": [
                "Power nap: 20 minutes only",
                "Walk around deck (safely!)",
                "Hydrate, eat protein snack",
                "Fresh air + sunlight",
            ],
            "anxiety": [
                "Progressive muscle relaxation",
                "Remind yourself: 'I've trained for this'",
                "Focus on next immediate action, not whole situation",
                "Talk to crew or to me (NAVI)",
            ],
        }

    async def initialize(self):
        """Initialize Ollama connection"""
        try:
            if self.mock_mode:
                logger.info("Running in MOCK MODE - using simple responses")
                return

            response = await self.client.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                logger.info(f"Ollama available with models: {model_names}")

                if self.model not in model_names:
                    logger.warning(f"Model {self.model} not found. Available: {model_names}")
                    asyncio.create_task(self._pull_model())
            else:
                logger.error(f"Ollama not available: {response.status_code}")
                self.mock_mode = True

        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            self.mock_mode = True

    async def _pull_model(self) -> None:
        """Attempt to pull the configured Ollama model."""
        try:
            logger.info(f"Attempting to pull model: {self.model}")
            response = await self.client.post(
                f"{self.ollama_url}/api/pull",
                json={"name": self.model, "stream": False},
                timeout=settings.OLLAMA_TIMEOUT,
            )
            if response.status_code == 200:
                logger.info(f"Model pulled successfully: {self.model}")
            else:
                logger.error(f"Failed to pull model {self.model}: {response.status_code}")
        except Exception as e:
            logger.error(f"Model pull error for {self.model}: {e}")

    async def chat(self, user_message: str, context: Optional[Dict] = None) -> str:
        """Main chat function - routes to appropriate handler"""
        # Detect message type
        message_type = self._detect_message_type(user_message)
        
        # Route to appropriate handler
        if message_type == "medical":
            response = await self._handle_medical_query(user_message, context)
        elif message_type == "wellness":
            response = await self._handle_wellness_query(user_message, context)
        elif message_type == "weather":
            response = await self._handle_weather_query(user_message, context)
        elif message_type == "navtex":
            response = await self._handle_navtex_query(user_message)
        else:
            response = await self._ollama_chat(user_message, context)

        # Add to history
        self.conversation_history.append(Message("user", user_message, message_type))
        self.conversation_history.append(Message("assistant", response, message_type))

        return response

    def _detect_message_type(self, message: str) -> str:
        """Detect if message is medical, wellness, weather, navtex, or general chat"""
        msg_lower = message.lower()
        
        if "navtex" in msg_lower or "nav tex" in msg_lower:
            return "navtex"
        
        medical_words = [
            "symptom", "pain", "bleed", "hurt", "sick", "wound", "hypothermia",
            "cardiac", "nausea", "fever", "medical", "doctor", "injury", "poison",
        ]
        wellness_words = [
            "mood", "feeling", "mental", "stress", "anxiety", "depressed", "lonely",
            "struggling", "coping", "wellness", "health", "morale",
        ]
        weather_words = [
            "weather", "wind", "temperature", "pressure", "storm", "forecast",
            "conditions", "rain", "snow", "ice", "cold",
        ]
        
        if any(word in msg_lower for word in medical_words):
            return "medical"
        elif any(word in msg_lower for word in wellness_words):
            return "wellness"
        elif any(word in msg_lower for word in weather_words):
            return "weather"
        else:
            return "chat"

    async def _handle_medical_query(self, message: str, context: Optional[Dict]) -> str:
        """Route medical questions to appropriate protocol"""
        symptom_keywords = {
            "hypothermia": ["cold", "shivering", "frostbite", "freeze"],
            "cardiac": ["chest", "heart", "pain", "breathe"],
            "bleeding": ["cut", "bleed", "wound", "blood"],
            "seasickness": ["nausea", "sick", "dizzy", "vomit"],
            "dehydration": ["thirst", "dehydrated", "dry"],
        }
        
        for condition, keywords in symptom_keywords.items():
            if any(kw in message.lower() for kw in keywords):
                protocol = self.medical_protocols.get(condition, {})
                severity = "mild"  # Enhanced with ML in production
                
                response = f"⚠️ MEDICAL ALERT: {condition.upper()} detected!\n\n"
                response += f"Protocol: {protocol.get(severity, 'Seek medical help')}\n\n"
                response += "I'M NOT A DOCTOR! This is basic guidance only. Seek real medical help ASAP if serious!"
                
                logger.warning(f"Medical query detected: {condition} - {message}")
                return response
        
        # Fallback to LLM for complex medical questions
        return await self._ollama_chat(f"Medical: {message}", context)

    async def _handle_wellness_query(self, message: str, context: Optional[Dict]) -> str:
        """Handle mood checks and mental health support"""
        response = "Hey! Let's check in.\n\n"
        
        # Store mood check
        self.mood_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "query": message,
        })
        
        strategies = self.coping_strategies.get("stress", [])
        response += "Some things that might help:\n"
        for strategy in strategies:
            response += f"• {strategy}\n"
        
        response += "\nRemember: Isolation is hard, but you're not alone. I'm here. 💙"
        
        logger.info(f"Wellness check: {len(self.mood_history)} total")
        return response

    async def _handle_weather_query(self, message: str, context: Optional[Dict]) -> str:
        """Handle weather questions"""
        if context and "wind_speed" in context:
            wind = context.get("wind_speed", 0)
            temp = context.get("water_temperature", "unknown")
            pressure = context.get("air_pressure", "unknown")
            
            response = f"🌊 WEATHER UPDATE!\n\n"
            response += f"Wind: {wind} knots\n"
            response += f"Water temp: {temp}°C\n"
            response += f"Pressure: {pressure} mb\n\n"
            
            if isinstance(wind, (int, float)) and wind > 25:
                response += "🚨 STRONG WINDS! Be careful out there!\n"
            elif isinstance(wind, (int, float)) and wind < 5:
                response += "Beautiful calm conditions! Enjoy it while it lasts.\n"
            else:
                response += "Decent sailing weather. Not too shabby!\n"
            
            return response
        
        return await self._ollama_chat(message, context)

    async def _handle_navtex_query(self, message: str) -> str:
        """Handle NAVTEX queries with brief summary or full report."""
        msg_lower = message.lower()
        wants_full = any(token in msg_lower for token in ["full", "details", "detail", "report", "raw", "all"])

        if wants_full:
            history = navigator.navigator.get_navtex_messages(limit=10)
            if not history:
                return "No NAVTEX messages on record."
            lines = ["NAVTEX FULL REPORT (last 10):"]
            for entry in history:
                coords = entry.get("coordinates", [])
                coord_text = ""
                if coords:
                    coord_text = f" coords={coords[0]}"
                content = entry.get("content", "").strip().replace("\n", " ")
                if len(content) > 160:
                    content = content[:160] + "..."
                lines.append(
                    f"- {entry.get('timestamp', '')} [{entry.get('severity', 'INFO')}] "
                    f"{entry.get('type', '')} {entry.get('id', '')}{coord_text}: {content}"
                )
            return "\n".join(lines)

        summary = navigator.navigator.get_navtex_summary(limit=10)
        total = summary.get("total", 0)
        if total == 0:
            return "NAVTEX summary: no messages on record."
        counts = summary.get("counts_by_severity", {})
        warnings = counts.get("WARNING", 0) + counts.get("CRITICAL", 0)
        latest = summary.get("latest") or {}
        latest_line = ""
        if latest:
            latest_line = (
                f"Latest: {latest.get('type', '')} {latest.get('id', '')} "
                f"[{latest.get('severity', '')}] at {latest.get('timestamp', '')}"
            )
        return (
            "NAVTEX summary (last 10): "
            f"{total} messages, {warnings} warnings. "
            f"{latest_line}"
        )

    async def _ollama_chat(self, user_message: str, context: Optional[Dict]) -> str:
        """Send message to Ollama"""
        if self.mock_mode:
            logger.info("Ollama in mock mode, returning mock response")
            return self._mock_response(user_message, context)

        try:
            # Ensure client is initialized
            if self.client.is_closed:
                logger.info("Re-initializing closed httpx client")
                self.client = httpx.AsyncClient(timeout=60.0)
            context_str = ""
            if context:
                context_str = "\n\nCURRENT SITUATION:\n"
                if "gps" in context:
                    context_str += f"Position: {context['gps']}\n"
                if "wind_speed" in context:
                    context_str += f"Wind: {context['wind_speed']} knots\n"
                if "threats" in context:
                    context_str += f"Threats: {context['threats']}\n"

            messages = [
                {"role": "system", "content": self.system_prompt},
            ]

            # Add recent history
            for msg in self.conversation_history[-10:]:
                messages.append({"role": msg.role, "content": msg.content})

            messages.append({"role": "user", "content": f"{context_str}\n\nUser: {user_message}"})

            response = await self.client.post(
                f"{self.ollama_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False},
            )

            if response.status_code == 200:
                return response.json()["message"]["content"]
            if response.status_code == 404:
                logger.warning(f"Ollama model not found: {self.model}. Attempting pull.")
                await self._pull_model()
                return "Model is downloading. Please try again in a moment."
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return "Error: I'm having trouble thinking right now. Try again in a moment."

        except Exception as e:
            logger.error(f"Chat error: {e}")
            self.mock_mode = True  # Switch to mock on failure
            return self._mock_response(user_message, context)

    def _mock_response(self, message: str, context: Optional[Dict]) -> str:
        """Simple rule-based mock responses for when Ollama is offline"""
        msg = message.lower()
        if "status" in msg:
            response = "Status: operational and monitoring all systems."
            if context:
                gps = context.get("gps")
                if gps:
                    response += f" Position: {gps}."
                cog = context.get("cog")
                sog = context.get("sog")
                if cog is not None:
                    response += f" Course: {cog}."
                if sog is not None:
                    response += f" Speed: {sog}."
                threats = context.get("threats")
                if threats is not None:
                    response += f" Threats detected: {len(threats)}."
            return response
        if "hello" in msg or "hi" in msg or "hey" in msg:
            return "Hey! I'm NAVI, your Arctic assistant! I'm currently running in low-power mode, but I can still help with medical, weather, and basic status!"
        if "threat" in msg or "danger" in msg:
            return "Threat report: no confirmed dangers at the moment. Vakten is watching for ice, ships, and obstacles."
        if "ice" in msg:
            return "Ice conditions: monitor closely. Watch for floes and bergs; Vakten will alert on detections."
        if "weather" in msg:
            return "The weather is... well, it's Arctic! Cold, crisp, and perfect for some exploration!"
        if "navtex" in msg:
            return "NAVTEX summary is not available in low-power mode."
        if "help" in msg:
            return "I can help you with medical triage, weather updates, and mental health support. Just ask!"
        
        return "Acknowledged. I'm in low-power mode (Ollama offline), but I can still assist with basics. HEY LISTEN!"

    def _get_mock_response(self, message: str) -> str:
        """Legacy mock response wrapper."""
        return self._mock_response(message, None)

    async def stream_chat(self, user_message: str, context: Optional[Dict] = None):
        """Stream chat response in chunks."""
        full_response = await self.chat(user_message, context)
        chunk_size = 24
        for i in range(0, len(full_response), chunk_size):
            yield full_response[i : i + chunk_size]

    async def anomaly_alert(
        self, threat_type: str, confidence: float, details: Optional[Dict] = None
    ) -> None:
        """Broadcast anomaly alert"""
        now = time.time()
        
        if now - self.last_anomaly_time < self.anomaly_cooldown:
            logger.debug("Anomaly alert suppressed (cooldown)")
            return
        
        self.last_anomaly_time = now
        
        alert_message = f"🚨 HEY LISTEN!!! 🚨\n\n"
        alert_message += f"THREAT DETECTED: {threat_type.upper()}!!!\n"
        alert_message += f"CONFIDENCE: {confidence*100:.0f}%\n\n"
        
        if threat_type == "ice":
            alert_message += "ICE FLOE DETECTED! HARD TO STARBOARD!\n"
        elif threat_type == "ship":
            alert_message += "ANOTHER VESSEL NEARBY! CHECK COLLISION RISK!\n"
        elif threat_type == "person":
            alert_message += "PERSON IN WATER!!! IMMEDIATE ACTION REQUIRED!!!\n"
        elif threat_type == "obstacle":
            alert_message += "OBSTACLE AHEAD! MANEUVER NOW!\n"
        
        if details:
            alert_message += f"\nDistance: {details.get('distance_m', 'unknown')}m\n"
            alert_message += f"Direction: {details.get('bearing_deg', 'unknown')}°\n"
        
        alert_message += "\n⚠️ CAPTAIN, THIS REQUIRES YOUR IMMEDIATE ATTENTION!"
        
        logger.critical(alert_message)
        self.conversation_history.append(Message("assistant", alert_message, "alert"))

    def get_status(self) -> Dict:
        """NAVI status report"""
        return {
            "module": "navi",
            "status": "ready",
            "roles": ["Doctor", "Weather Girl", "Anomaly Screamer", "Friend"],
            "mock_mode": self.mock_mode,
            "model": self.model,
            "ollama_url": self.ollama_url,
            "mood_checks": len(self.mood_history),
            "conversation_length": len(self.conversation_history),
            "version": "Merged Doctor+Weather+Screamer",
        }

    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get conversation history"""
        return [msg.to_dict() for msg in self.conversation_history[-limit:]]

    async def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    async def close(self):
        """Close connections"""
        await self.client.aclose()
        logger.info("Navi connections closed")


# Global instance
navi = NaviModule(ollama_url=settings.OLLAMA_BASE_URL, mock_mode=False)

