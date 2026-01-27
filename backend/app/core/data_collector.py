"""
Data Collection Framework for AADS
Collects data for YOLO training, Ollama fine-tuning, and module consolidation
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DataCollector:
    """Manages data collection for training and fine-tuning"""

    def __init__(self, base_path: str = "data/collected"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.yolo_path = self.base_path / "yolo"
        self.ollama_path = self.base_path / "ollama"
        self.health_path = self.base_path / "health_wellness"
        self.systems_path = self.base_path / "systems_resources"

        for path in [self.yolo_path, self.ollama_path, self.health_path, self.systems_path]:
            path.mkdir(parents=True, exist_ok=True)

        logger.info(f"DataCollector initialized at {self.base_path}")

    # ====== YOLO VISION DATA ======

    def create_yolo_annotation(
        self,
        image_filename: str,
        detections: List[Dict],
        image_metadata: Optional[Dict] = None,
    ) -> str:
        """
        Create YOLO format annotation (.txt file)
        
        Format: <class_id> <x_center> <y_center> <width> <height> (normalized 0-1)
        Classes:
            0: ice_floe
            1: ship
            2: person
            3: obstacle
            4: buoy
            5: whale
            6: seal
            7: debris
        """
        class_names = ["ice_floe", "ship", "person", "obstacle", "buoy", "whale", "seal", "debris"]
        
        annotation_lines = []
        for det in detections:
            class_name = det.get("class")
            if class_name not in class_names:
                logger.warning(f"Unknown class: {class_name}")
                continue
            
            class_id = class_names.index(class_name)
            x_center = det.get("x_center")
            y_center = det.get("y_center")
            width = det.get("width")
            height = det.get("height")
            
            # Validate normalized coordinates
            if not all(0 <= v <= 1 for v in [x_center, y_center, width, height]):
                logger.error(f"Invalid normalized coordinates: {det}")
                continue
            
            annotation_lines.append(f"{class_id} {x_center} {y_center} {width} {height}")
        
        # Save annotation
        txt_filename = image_filename.rsplit(".", 1)[0] + ".txt"
        annotation_path = self.yolo_path / "annotations" / txt_filename
        annotation_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(annotation_path, "w") as f:
            f.write("\n".join(annotation_lines))
        
        # Save metadata
        if image_metadata:
            metadata_path = self.yolo_path / "metadata" / (txt_filename.rsplit(".", 1)[0] + ".json")
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_path, "w") as f:
                json.dump({
                    "filename": image_filename,
                    "timestamp": datetime.utcnow().isoformat(),
                    "detections_count": len(detections),
                    **image_metadata
                }, f, indent=2)
        
        return str(annotation_path)

    def create_yolo_dataset_config(self, train_split: float = 0.8, val_split: float = 0.1):
        """Create YOLO dataset.yaml configuration"""
        dataset_config = {
            "path": str(self.yolo_path),
            "train": "images/train",
            "val": "images/val",
            "test": "images/test",
            "nc": 8,
            "names": ["ice_floe", "ship", "person", "obstacle", "buoy", "whale", "seal", "debris"]
        }
        
        config_path = self.yolo_path / "dataset.yaml"
        with open(config_path, "w") as f:
            json.dump(dataset_config, f, indent=2)
        
        return str(config_path)

    # ====== OLLAMA FINE-TUNING DATA ======

    def create_ollama_training_pair(
        self,
        question: str,
        answer: str,
        category: str,
        source: str = "manual"
    ) -> Dict:
        """Create Q&A pair for Ollama fine-tuning"""
        pair = {
            "question": question,
            "answer": answer,
            "category": category,
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return pair

    def save_ollama_training_data(self, pairs: List[Dict], filename: str = "training_data.jsonl"):
        """Save training pairs in JSONL format for Ollama fine-tuning"""
        output_path = self.ollama_path / filename
        
        with open(output_path, "a") as f:
            for pair in pairs:
                f.write(json.dumps(pair) + "\n")
        
        logger.info(f"Saved {len(pairs)} training pairs to {output_path}")
        return str(output_path)

    def get_ollama_training_templates(self) -> Dict[str, List[Dict]]:
        """Get templates for common Arctic maritime Q&A"""
        return {
            "navigation": [
                {
                    "question": "What is the current course?",
                    "answer": "Monitor heading indicator. Current course is [heading]°. Adjust as needed based on sea state and winds.",
                    "category": "navigation"
                },
                {
                    "question": "How do I avoid ice?",
                    "answer": "Monitor Vakten vision system for ice floes. Reduce speed in ice-prone areas. Check ice charts before departure.",
                    "category": "navigation"
                },
            ],
            "safety": [
                {
                    "question": "What's the emergency protocol?",
                    "answer": "1) Sound alarm. 2) Alert all crew. 3) Prepare life jackets. 4) Assess situation. 5) Contact Coast Guard if needed.",
                    "category": "safety"
                },
                {
                    "question": "What should I do if I see another vessel?",
                    "answer": "Monitor distance and bearing. Apply collision avoidance rules. Give way if required. Maintain communication on VHF.",
                    "category": "safety"
                },
            ],
            "maintenance": [
                {
                    "question": "How often should systems be checked?",
                    "answer": "Daily: Engine, fuel, water. Weekly: All systems self-test. Monthly: Full diagnostics. Record all maintenance in log.",
                    "category": "maintenance"
                },
                {
                    "question": "What's the engine status?",
                    "answer": "Check Ingenioren module for real-time engine diagnostics. Monitor fuel consumption and temperature.",
                    "category": "maintenance"
                },
            ],
            "health": [
                {
                    "question": "What should I do if someone is injured?",
                    "answer": "1) Assess injury severity. 2) Provide first aid if trained. 3) Contact medical assistance. 4) Document in health log.",
                    "category": "health"
                },
                {
                    "question": "How do I manage seasickness?",
                    "answer": "Rest in well-ventilated area. Stay hydrated. Focus on horizon. Medication available in medical kit. Consult Legen module.",
                    "category": "health"
                },
            ],
            "psychology": [
                {
                    "question": "How do I stay mentally prepared for Arctic operations?",
                    "answer": "Maintain regular sleep schedule. Exercise when possible. Regular breaks from watch. Check in with crew. Consult Psykologen module.",
                    "category": "psychology"
                },
                {
                    "question": "What should I do if I feel stressed?",
                    "answer": "Talk to crew or counselor. Take measured breaks. Practice relaxation techniques. Consult Psykologen module for support.",
                    "category": "psychology"
                },
            ],
            "resources": [
                {
                    "question": "How much fuel do we have?",
                    "answer": "Check Systems & Resources dashboard for fuel levels. Current consumption rate is [rate] L/hour.",
                    "category": "resources"
                },
                {
                    "question": "What supplies are we low on?",
                    "answer": "Consult inventory system. Order fresh supplies at next port. Check Systems & Resources module for stock levels.",
                    "category": "resources"
                },
            ],
        }

    # ====== HEALTH & WELLNESS DATA (Legen + Psykologen) ======

    def create_health_record(
        self,
        crew_id: str,
        vital_signs: Dict,
        notes: str,
        record_type: str = "health"  # health, psychological, fitness
    ) -> Dict:
        """Create health record for combined Legen + Psykologen module"""
        return {
            "crew_id": crew_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": record_type,
            "vital_signs": vital_signs,
            "notes": notes
        }

    def save_health_records(self, records: List[Dict], filename: str = "health_records.jsonl"):
        """Save health records"""
        output_path = self.health_path / filename
        
        with open(output_path, "a") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")
        
        return str(output_path)

    # ====== SYSTEMS & RESOURCES DATA (Quartermaster + Ingenioren) ======

    def create_system_log(
        self,
        system: str,
        status: str,
        details: Dict,
        severity: str = "info"  # info, warning, critical
    ) -> Dict:
        """Create system/resource log for combined Systems & Resources module"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": system,
            "status": status,
            "severity": severity,
            "details": details
        }

    def save_system_logs(self, logs: List[Dict], filename: str = "system_logs.jsonl"):
        """Save system logs"""
        output_path = self.systems_path / filename
        
        with open(output_path, "a") as f:
            for log in logs:
                f.write(json.dumps(log) + "\n")
        
        return str(output_path)

    # ====== DATA STATISTICS ======

    def get_collection_stats(self) -> Dict:
        """Get statistics on collected data"""
        stats = {
            "yolo": {
                "annotations": len(list(self.yolo_path.glob("annotations/*.txt"))),
                "images": len(list(self.yolo_path.glob("images/**/*.jpg"))) + len(list(self.yolo_path.glob("images/**/*.png"))),
            },
            "ollama": {
                "training_pairs": 0
            },
            "health": {
                "records": len(list(self.health_path.glob("*.jsonl")))
            },
            "systems": {
                "logs": len(list(self.systems_path.glob("*.jsonl")))
            }
        }
        
        # Count JSONL lines
        try:
            for jsonl_file in self.ollama_path.glob("*.jsonl"):
                with open(jsonl_file) as f:
                    stats["ollama"]["training_pairs"] += sum(1 for _ in f)
        except Exception as e:
            logger.error(f"Error counting training pairs: {e}")
        
        return stats

    def export_for_training(self, format: str = "yolo") -> str:
        """Export data in training format"""
        if format == "yolo":
            export_path = self.yolo_path / "export"
            export_path.mkdir(exist_ok=True)
            logger.info(f"YOLO data ready at {export_path}")
            return str(export_path)
        elif format == "ollama":
            export_path = self.ollama_path / "training_data.jsonl"
            logger.info(f"Ollama training data at {export_path}")
            return str(export_path)
        else:
            raise ValueError(f"Unknown format: {format}")


if __name__ == "__main__":
    collector = DataCollector()
    print(f"Data collection framework initialized at {collector.base_path}")
