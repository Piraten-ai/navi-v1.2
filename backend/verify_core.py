#!/usr/bin/env python3
"""Verification script for AADS backend core setup."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test all core imports."""
    print("=" * 60)
    print("AADS Backend Core Verification")
    print("=" * 60)
    print()
    
    try:
        print("1. Testing Configuration...")
        from app.core.config import settings
        print(f"   ✓ Settings loaded")
        print(f"   ✓ App: {settings.APP_NAME} v{settings.APP_VERSION}")
        print(f"   ✓ Environment: {settings.ENVIRONMENT}")
        print(f"   ✓ DEV_MODE: {settings.DEV_MODE}")
        print()
        
        print("2. Testing Logging...")
        from app.core.logging import get_logger, get_contextual_logger, log_exception
        logger = get_logger("test")
        print(f"   ✓ Logger created: {logger.name}")
        ctx_logger = get_contextual_logger("test.ctx", test_id=123)
        print(f"   ✓ Contextual logger created")
        print()
        
        print("3. Testing Dependencies...")
        from app.core.dependencies import (
            get_database_engine,
            get_session_maker,
            verify_system_health,
            DatabaseDep,
            RedisDep,
            LoggerDep,
        )
        print(f"   ✓ Database dependencies available")
        print(f"   ✓ Redis dependencies available")
        print(f"   ✓ Logger dependencies available")
        print()
        
        print("4. Testing FastAPI Application...")
        from app.main import app, connection_manager
        print(f"   ✓ FastAPI app created")
        print(f"   ✓ App title: {app.title}")
        print(f"   ✓ Connection manager ready")
        
        # Count routes
        routes = [r for r in app.routes if hasattr(r, 'path')]
        print(f"   ✓ Routes: {len(routes)} registered")
        print()
        
        print("5. Verifying Core Files...")
        files = [
            "app/__init__.py",
            "app/main.py",
            "app/core/__init__.py",
            "app/core/config.py",
            "app/core/dependencies.py",
            "app/core/logging.py",
            "app/modules/__init__.py",
        ]
        
        for file in files:
            path = Path(file)
            if path.exists():
                size = path.stat().st_size
                print(f"   ✓ {file} ({size} bytes)")
            else:
                print(f"   ✗ {file} MISSING!")
                return False
        print()
        
        print("6. Configuration Summary...")
        print(f"   • Database: {settings.DATABASE_URL}")
        print(f"   • Redis: {settings.REDIS_URL}")
        print(f"   • Ollama: {settings.OLLAMA_BASE_URL}")
        print(f"   • Log Level: {settings.LOG_LEVEL}")
        print(f"   • Mock Camera: {settings.MOCK_CAMERA}")
        print(f"   • CORS Origins: {len(settings.CORS_ORIGINS)}")
        print(f"   • WS Max Connections: {settings.WS_MAX_CONNECTIONS}")
        print()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Run: uvicorn app.main:app --reload")
        print("  2. Visit: http://localhost:8000/api/v1/docs")
        print("  3. Check: http://localhost:8000/health")
        print("  4. Test WebSocket: ws://localhost:8000/ws")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
