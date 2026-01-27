"""
Legen (The Doctor) - Medical Triage & Support Module
Maritime medical assistance and emergency protocols
"""

from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LegenModule:
    """Medical triage and support"""

    def __init__(self):
        self.assessments: List[Dict] = []
        self.protocols = self._load_protocols()
        logger.info("Legen initialized")

    def _load_protocols(self) -> Dict:
        """Load maritime medical protocols - comprehensive guidelines"""
        return {
            "hypothermia": {
                "mild": {
                    "core_temp": "32-35°C (90-95°F)",
                    "signs": "Shivering, confusion, mild disorientation",
                    "treatment": "Remove wet clothing, wrap in blankets, warm (NOT HOT) drinks, monitor vitals constantly",
                    "evacuation": "Medical evaluation recommended",
                },
                "moderate": {
                    "core_temp": "28-32°C (82-90°F)",
                    "signs": "Shivering stops, confusion, slurred speech, drowsiness",
                    "treatment": "Horizontal position (prevent afterdrop), remove wet clothing, warm blankets, warm beverages if conscious, avoid friction, monitor for arrhythmia",
                    "evacuation": "RECOMMENDED - medical facility needed",
                    "critical": "DO NOT rub skin. Avoid rapid rewarming.",
                },
                "severe": {
                    "core_temp": "<28°C (<82°F)",
                    "signs": "Loss of consciousness, barely detectable pulse, rigid limbs",
                    "treatment": "MEDEVAC REQUIRED. Gentle handling (very fragile), horizontal, passive rewarming only, monitor for VF, prepare for prolonged CPR if needed",
                    "evacuation": "IMMEDIATE - helicopter or fast boat",
                    "critical": "Patient not dead until warm and dead. Can recover from extreme hypothermia.",
                },
            },
            "cold_water_immersion": {
                "0_3_min": "Cold shock - involuntary gasping, hyperventilation. Exit water immediately.",
                "3_30_min": "Cold incapacitation - 50% loss of grip strength, hypothermia begins",
                "30_min_plus": "Hypothermia onset, time in water is critical survival factor",
                "prevention": "Immersion suit, lifejacket, cold water training, buddy system",
                "rescue": "Handle carefully - rough handling triggers fatal arrhythmia. Keep horizontal.",
            },
            "seasickness": {
                "mild": "Nausea, slight dizziness, pale",
                "moderate": "Vomiting, dizziness, sweating, unable to work",
                "severe": "Incapacitating, dehydration risk",
                "prevention": "Ginger supplements, acupressure bands, Dramamine, central cabin location, focus horizon",
                "treatment": "Rest in calm area, small frequent meals (ginger biscuits), electrolyte fluids, fresh air, Ondansetron if available",
                "note": "Rarely life-threatening but risk of dehydration and falls",
            },
            "trauma_bleeding": {
                "arterial": {
                    "signs": "Bright red, spurting, rapid flow",
                    "treatment": "1) Firm direct pressure (10-15 min). 2) Elevation. 3) Pressure points. 4) Tourniquet 2-3 inches above wound. 5) MEDEVAC URGENT",
                    "tourniquet": "Mark time applied. Check every 30 min. Remove only in OR.",
                },
                "venous": {
                    "signs": "Dark red, steady flow",
                    "treatment": "Direct pressure, elevation, pressure dressing, monitor for shock",
                },
                "severe": "IV access if trained, keep warm, horizontal, elevate legs, oxygen, MEDEVAC URGENT",
            },
            "fractures": {
                "general": "RICE protocol (Rest, Ice, Compression, Elevation), immobilize, pain control",
                "femur": "LIFE-THREATENING (fat embolism). Traction splint, IV fluids, MEDEVAC URGENT",
                "pelvis": "LIFE-THREATENING (massive bleeding). Pelvic binder, IV fluids, MEDEVAC URGENT",
                "spine": "IMMOBILIZE immediately. Avoid twisting. Log roll turns only. MEDEVAC URGENT",
                "open_fracture": "Cover wound, tourniquet if bleeding, IV antibiotics, MEDEVAC URGENT",
            },
            "burns": {
                "minor": "<10% body. Cool water (NOT ice) 10-20 min, aloe vera, sterile dressing, pain relief",
                "moderate": "10-20% body. Cool water, IV fluids (Parkland: 4mL × kg × %burn over 24h), pain control, MEDEVAC recommended",
                "severe": ">20% body. Cool water CAREFULLY, IV fluids LARGE bore, oxygen, pain control, MEDEVAC URGENT",
                "critical": "Never ice directly. Avoid hypothermia. Calculate fluid replacement. Watch airway.",
            },
            "cardiac": {
                "chest_pain": {
                    "immediate": "Sit/lie down, rest, ASPIRIN 325mg (if not allergic), oxygen if available",
                    "treatment": "Monitor vitals, keep warm, reassure, prepare CPR",
                    "evacuation": "MEDEVAC URGENT - treat as MI until proven otherwise",
                },
                "cpr": {
                    "rate": "100-120 compressions/min (push hard/fast)",
                    "depth": "Adult: 2-2.4 inches (5-6cm), heel of hand on sternum",
                    "ventilation": "30 compressions : 2 breaths (or continuous if untrained)",
                    "duration": "Continue until: patient revives, professional takes over, you're exhausted",
                    "note": "Survival 1-3% after 30+ min. Never give up.",
                },
            },
            "respiratory": {
                "drowning": {
                    "immediate": "Remove from water, clear airway, begin CPR",
                    "treatment": "CPR, oxygen, monitor for pulmonary edema (pink frothy sputum)",
                    "note": "Cold water protects brain. People recovered after 30+ min submersion.",
                },
                "choking": "5 back blows + 5 abdominal thrusts, repeat until dislodged or unconscious (then CPR)",
                "asthma": "Rescue inhaler (2 puffs), sit upright, calm. If no improvement 10 min or severe, MEDEVAC",
                "pneumothorax": "Chest pain, SOB, unequal breath sounds. Tape chest, oxygen, MEDEVAC URGENT",
            },
            "infection": {
                "wound_care": "Clean with fresh water, remove debris, antibiotic ointment, sterile dressing",
                "signs": "Redness, warmth, swelling, pus, fever, red streaks",
                "antibiotics": "Amoxicillin-clavulanate for contaminated wounds, fluoroquinolone alternative",
                "tetanus": "Update booster if needed after injury",
            },
            "shock": {
                "signs": "Pale, cold, sweaty, weak pulse, rapid breathing, confusion, low BP",
                "treatment": "1) Horizontal, elevate legs 6-12 inches. 2) Keep warm. 3) IV fluids. 4) Oxygen. 5) MEDEVAC URGENT",
                "types": "Hypovolemic (bleeding), cardiogenic (heart), septic (infection), anaphylactic (allergen)",
            },
        }

    def assess(self, symptoms: List[str], severity: str = "medium") -> Dict:
        """Assess symptoms and provide guidance"""
        assessment = {
            "timestamp": datetime.utcnow().isoformat(),
            "symptoms": symptoms,
            "severity": severity,
            "triage_level": self._triage(symptoms, severity),
            "recommendations": [],
            "evacuation_needed": False,
        }

        # Check for critical symptoms
        critical_symptoms = ["chest_pain", "difficulty_breathing", "unconscious", "severe_bleeding", "severe_hypothermia"]

        if any(s in symptoms for s in critical_symptoms):
            assessment["triage_level"] = "RED"
            assessment["evacuation_needed"] = True
            assessment["recommendations"].append("IMMEDIATE EVACUATION REQUIRED")

        # Hypothermia check
        if "hypothermia" in symptoms or "cold" in symptoms:
            if severity == "severe":
                assessment["protocol"] = self.protocols["hypothermia"]["severe"]
            elif severity == "medium":
                assessment["protocol"] = self.protocols["hypothermia"]["moderate"]
            else:
                assessment["protocol"] = self.protocols["hypothermia"]["mild"]

        # Trauma check
        if "bleeding" in symptoms:
            assessment["protocol"] = self.protocols["trauma"]["bleeding"]

        if "fracture" in symptoms or "broken" in symptoms:
            assessment["protocol"] = self.protocols["trauma"]["fracture"]

        # Cardiac
        if "chest_pain" in symptoms:
            assessment["protocol"] = self.protocols["cardiac"]["chest_pain"]
            assessment["evacuation_needed"] = True

        # Seasickness
        if "seasickness" in symptoms or "nausea" in symptoms:
            assessment["protocol"] = self.protocols["seasickness"]["treatment"]

        # General recommendations
        assessment["recommendations"].extend(
            [
                "Monitor vital signs every 15 minutes",
                "Document all treatments administered",
                "Prepare medical report for evacuation",
            ]
        )

        self.assessments.append(assessment)
        logger.info(f"Medical assessment completed: {assessment['triage_level']}")

        return assessment

    def _triage(self, symptoms: List[str], severity: str) -> str:
        """Triage level determination (RED/YELLOW/GREEN)"""
        critical = ["chest_pain", "unconscious", "severe_bleeding", "difficulty_breathing"]
        urgent = ["fracture", "burns", "severe_pain", "hypothermia"]

        if any(s in symptoms for s in critical) or severity == "critical":
            return "RED"  # Immediate
        elif any(s in symptoms for s in urgent) or severity == "high":
            return "YELLOW"  # Urgent
        else:
            return "GREEN"  # Non-urgent

    def get_protocol(self, protocol_type: str) -> Dict:
        """Get specific medical protocol"""
        return self.protocols.get(protocol_type, {"error": "Protocol not found"})

    def get_status(self) -> Dict:
        """Get module status"""
        return {
            "module": "legen",
            "status": "ready",
            "total_assessments": len(self.assessments),
            "red_triage": len([a for a in self.assessments if a["triage_level"] == "RED"]),
            "protocols_available": len(self.protocols),
        }


# Global instance
legen = LegenModule()
