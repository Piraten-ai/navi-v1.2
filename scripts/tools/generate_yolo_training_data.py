#!/usr/bin/env python3
"""
AADS Synthetic YOLO Training - Quick Start
Generate 500+ Arctic maritime training images in 5 minutes
Philosophy: "When satellites fail, we survive" - Vakten (The Guard)
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    print(
        """
==============================================================
AADS YOLO SYNTHETIC DATA GENERATION
Arctic Maritime Threat Detection Training Data
Philosophy: Offline-First Edge AI for Polar Resilience
Vakten (The Guard) - Local Vision Intelligence
Ready for YOLOv8 training on NVIDIA Jetson Orin
==============================================================
"""
    )

    try:
        root = Path(__file__).resolve().parents[2]
        os.chdir(root)

        sys.path.insert(0, str(root / "backend"))
        from app.core.synthetic_yolo_generator import ArcticYOLOGenerator

        logger.info("Initializing ArcticYOLOGenerator...")
        generator = ArcticYOLOGenerator(output_path="data/collected/yolo")

        logger.info("Generating 500 synthetic Arctic maritime images...")
        logger.info("Classes: ice_floe, ship, person, obstacle, buoy, whale, seal, debris")
        logger.info("")

        stats = generator.generate_dataset(num_images=500)
        generator.print_summary(stats)

        print("\nDATASET GENERATION COMPLETE\n")
        print("Next Steps:")
        print("1. Train YOLOv8 model:")
        print(
            "   python -c \"from ultralytics import YOLO; "
            "YOLO('yolov8m.pt').train(data='data/collected/yolo/dataset.yaml', epochs=100)\""
        )
        print("\n2. Deploy to Vakten module:")
        print("   cp runs/detect/train/weights/best.pt backend/app/modules/vakten/models/yolov8_arctic.pt")
        print("\n3. Start inference:")
        print("   docker compose up -d && curl http://localhost:8000/api/modules/vakten/camera/stream")
        print("\n" + "=" * 70)
        print("Philosophy: 'When satellites fail, we survive'")
        print("=" * 70 + "\n")

        return 0
    except Exception as e:
        logger.error("Generation failed: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
