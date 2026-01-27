#!/usr/bin/env python3
"""
Local test runner for AADS backend tests without Docker.
This script sets up a minimal test environment and runs pytest.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run tests locally without Docker."""
    backend_dir = Path(__file__).parent
    tests_dir = backend_dir / "tests"
    
    print("=" * 70)
    print("AADS Backend Test Runner (Local)")
    print("=" * 70)
    print()
    
    # Check if pytest is installed
    try:
        import pytest
        print(f"✓ pytest version: {pytest.__version__}")
    except ImportError:
        print("✗ pytest not found. Installing test dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-q", 
            "-r", str(tests_dir / "requirements-test.txt")
        ], check=True)
        import pytest
        print(f"✓ pytest version: {pytest.__version__}")
    
    print()
    print("Running tests...")
    print("-" * 70)
    print()
    
    # Run pytest
    pytest_args = [
        str(tests_dir / "test_models_quick.py"),
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    result = pytest.main(pytest_args)
    
    print()
    print("=" * 70)
    if result == 0:
        print("✓ All tests passed!")
    else:
        print(f"✗ Tests failed with exit code: {result}")
    print("=" * 70)
    
    return result

if __name__ == "__main__":
    sys.exit(main())
