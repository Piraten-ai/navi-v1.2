"""
Module Consolidation Framework
Combines:
- Legen (Doctor) + Psykologen (Shrink) = Health & Wellness
- Quartermaster (lost) + Ingenioren (Engineer) = Systems & Resources
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HealthWellnessModule:
    """Combined Health & Wellness (Legen + Psykologen)"""

    def __init__(self):
        self.crew_records: Dict[str, List[Dict]] = {}
        self.mental_health_notes: List[Dict] = []
        self.fitness_logs: List[Dict] = []
        
        logger.info("Health & Wellness module initialized (Legen + Psykologen)")

    def record_vital_signs(
        self,
        crew_id: str,
        heart_rate: int,
        blood_pressure: str,
        temperature: float,
        notes: str = ""
    ) -> Dict:
        """Record crew vital signs (Legen function)"""
        record = {
            "crew_id": crew_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "vitals",
            "heart_rate": heart_rate,
            "blood_pressure": blood_pressure,
            "temperature": temperature,
            "notes": notes
        }
        
        if crew_id not in self.crew_records:
            self.crew_records[crew_id] = []
        self.crew_records[crew_id].append(record)
        
        return record

    def assess_mental_health(
        self,
        crew_id: str,
        stress_level: int,  # 1-10
        sleep_quality: int,  # 1-10
        mood: str,  # good, neutral, poor
        notes: str = ""
    ) -> Dict:
        """Assess crew mental health (Psykologen function)"""
        assessment = {
            "crew_id": crew_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "mental_health",
            "stress_level": stress_level,
            "sleep_quality": sleep_quality,
            "mood": mood,
            "notes": notes
        }
        
        self.mental_health_notes.append(assessment)
        
        # Alert if stress is critical
        if stress_level >= 8:
            logger.warning(f"HIGH STRESS ALERT: {crew_id} stress level {stress_level}/10")
        
        return assessment

    def log_fitness_activity(
        self,
        crew_id: str,
        activity: str,
        duration_minutes: int,
        intensity: str  # light, moderate, intense
    ) -> Dict:
        """Log crew fitness activity (integrated function)"""
        activity_log = {
            "crew_id": crew_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "fitness",
            "activity": activity,
            "duration_minutes": duration_minutes,
            "intensity": intensity
        }
        
        self.fitness_logs.append(activity_log)
        return activity_log

    def get_crew_health_report(self, crew_id: str) -> Dict:
        """Get comprehensive health report for crew member"""
        vitals = self.crew_records.get(crew_id, [])
        mental = [m for m in self.mental_health_notes if m.get("crew_id") == crew_id]
        fitness = [f for f in self.fitness_logs if f.get("crew_id") == crew_id]
        
        # Get latest readings
        latest_vitals = vitals[-1] if vitals else None
        latest_mental = mental[-1] if mental else None
        
        health_score = 100
        warnings = []
        
        if latest_vitals:
            if latest_vitals["heart_rate"] > 100:
                warnings.append("Elevated heart rate")
                health_score -= 10
        
        if latest_mental:
            if latest_mental["stress_level"] >= 7:
                warnings.append("High stress level")
                health_score -= 15
            if latest_mental["sleep_quality"] <= 3:
                warnings.append("Poor sleep quality")
                health_score -= 10
        
        return {
            "crew_id": crew_id,
            "health_score": max(0, health_score),
            "latest_vitals": latest_vitals,
            "latest_mental_assessment": latest_mental,
            "fitness_activities": len(fitness),
            "warnings": warnings,
            "recommendation": self._get_recommendation(health_score, warnings)
        }

    def _get_recommendation(self, health_score: int, warnings: List[str]) -> str:
        """Get health recommendation based on score and warnings"""
        if health_score >= 85:
            return "Crew member in good health. Continue current routine."
        elif health_score >= 70:
            return "Minor concerns detected. Recommend rest and monitor vitals."
        elif health_score >= 50:
            return "Significant health concerns. Schedule medical review."
        else:
            return "CRITICAL: Immediate medical attention required."

    def get_status(self) -> Dict:
        """Get module status"""
        return {
            "module": "health_wellness",
            "status": "ready",
            "crew_tracked": len(self.crew_records),
            "total_vital_signs": sum(len(v) for v in self.crew_records.values()),
            "mental_assessments": len(self.mental_health_notes),
            "fitness_logs": len(self.fitness_logs)
        }


class SystemsResourcesModule:
    """Combined Systems & Resources (Ingenioren + Quartermaster)"""

    def __init__(self):
        self.system_status: Dict[str, Dict] = {}
        self.resource_inventory: Dict[str, float] = {}
        self.maintenance_logs: List[Dict] = []
        self.supply_orders: List[Dict] = []
        
        # Initialize critical systems
        self.systems = {
            "engine": {"status": "ready", "temperature": 0},
            "generator": {"status": "ready", "load": 0},
            "hydraulics": {"status": "ready", "pressure": 0},
            "navigation": {"status": "ready", "active": True},
            "communication": {"status": "ready", "signal": 0},
            "ballast": {"status": "ready", "level": 0},
            "pumps": {"status": "ready", "flow": 0}
        }
        
        # Initialize resource inventory
        self.resources = {
            "fuel": 0.0,  # liters
            "fresh_water": 0.0,  # liters
            "food": 0.0,  # kg
            "medical_supplies": 0.0,  # kg
            "spare_parts": 0.0  # kg
        }
        
        logger.info("Systems & Resources module initialized (Ingenioren + Quartermaster)")

    def update_system_status(
        self,
        system: str,
        status: str,
        details: Optional[Dict] = None
    ) -> Dict:
        """Update system status (Ingenioren function)"""
        if system not in self.systems:
            logger.warning(f"Unknown system: {system}")
            return {}
        
        update = {
            "system": system,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "details": details or {}
        }
        
        self.systems[system]["status"] = status
        if details:
            self.systems[system].update(details)
        
        # Log maintenance event if status is not ready
        if status != "ready":
            self.log_maintenance(system, status, details)
        
        return update

    def log_maintenance(
        self,
        system: str,
        action: str,
        notes: str = ""
    ) -> Dict:
        """Log maintenance action (Ingenioren function)"""
        maintenance_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": system,
            "action": action,
            "notes": notes
        }
        
        self.maintenance_logs.append(maintenance_log)
        logger.info(f"Maintenance logged: {system} - {action}")
        
        return maintenance_log

    def update_resource_level(
        self,
        resource: str,
        quantity: float,
        unit: str = "liters"
    ) -> Dict:
        """Update resource level (Quartermaster function)"""
        if resource not in self.resources:
            logger.warning(f"Unknown resource: {resource}")
            return {}
        
        old_level = self.resources[resource]
        self.resources[resource] = quantity
        
        update = {
            "timestamp": datetime.utcnow().isoformat(),
            "resource": resource,
            "old_level": old_level,
            "new_level": quantity,
            "unit": unit
        }
        
        # Check for low inventory
        if quantity < self._get_minimum_threshold(resource):
            logger.warning(f"LOW INVENTORY: {resource} at {quantity} {unit}")
            self._suggest_resupply(resource)
        
        return update

    def order_supplies(
        self,
        resource: str,
        quantity: float,
        destination: str,
        priority: str = "normal"  # normal, urgent
    ) -> Dict:
        """Create supply order (Quartermaster function)"""
        order = {
            "timestamp": datetime.utcnow().isoformat(),
            "resource": resource,
            "quantity": quantity,
            "destination": destination,
            "priority": priority,
            "status": "pending"
        }
        
        self.supply_orders.append(order)
        logger.info(f"Supply order created: {quantity} {resource} to {destination} ({priority})")
        
        return order

    def get_system_diagnostics(self) -> Dict:
        """Get comprehensive system diagnostics"""
        diagnostics = {
            "timestamp": datetime.utcnow().isoformat(),
            "systems": {},
            "alerts": []
        }
        
        for system, status in self.systems.items():
            diagnostics["systems"][system] = status
            
            if status["status"] != "ready":
                diagnostics["alerts"].append(f"{system.upper()}: {status['status']}")
        
        # Add resource warnings
        for resource, level in self.resources.items():
            if level < self._get_minimum_threshold(resource):
                diagnostics["alerts"].append(f"LOW: {resource} at {level}")
        
        return diagnostics

    def get_resource_report(self) -> Dict:
        """Get detailed resource report (Quartermaster view)"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "inventory": {},
            "pending_orders": [],
            "recommendations": []
        }
        
        for resource, level in self.resources.items():
            min_threshold = self._get_minimum_threshold(resource)
            report["inventory"][resource] = {
                "current": level,
                "minimum": min_threshold,
                "status": "good" if level > min_threshold * 1.5 else "low" if level < min_threshold else "adequate"
            }
        
        # List pending orders
        report["pending_orders"] = [o for o in self.supply_orders if o["status"] == "pending"]
        
        # Generate recommendations
        report["recommendations"] = self._get_resource_recommendations()
        
        return report

    def _get_minimum_threshold(self, resource: str) -> float:
        """Get minimum inventory threshold for resource"""
        thresholds = {
            "fuel": 500.0,  # liters
            "fresh_water": 200.0,  # liters
            "food": 50.0,  # kg
            "medical_supplies": 10.0,  # kg
            "spare_parts": 20.0  # kg
        }
        return thresholds.get(resource, 0)

    def _suggest_resupply(self, resource: str) -> None:
        """Suggest resupply order"""
        logger.warning(f"RESUPPLY SUGGESTION: {resource} inventory low")

    def _get_resource_recommendations(self) -> List[str]:
        """Generate resource management recommendations"""
        recommendations = []
        
        for resource, level in self.resources.items():
            min_threshold = self._get_minimum_threshold(resource)
            if level < min_threshold:
                recommendations.append(f"URGENT: Order {resource} at next port")
            elif level < min_threshold * 1.5:
                recommendations.append(f"Plan resupply of {resource} soon")
        
        return recommendations

    def get_status(self) -> Dict:
        """Get module status"""
        critical_systems = sum(1 for s in self.systems.values() if s["status"] != "ready")
        
        return {
            "module": "systems_resources",
            "status": "ready" if critical_systems == 0 else "warning",
            "systems_critical": critical_systems,
            "total_systems": len(self.systems),
            "maintenance_logs": len(self.maintenance_logs),
            "pending_orders": len([o for o in self.supply_orders if o["status"] == "pending"])
        }


# Global instances
health_wellness = HealthWellnessModule()
systems_resources = SystemsResourcesModule()
