#!/usr/bin/env python
"""
CrisisGrid Backend Engine - Startup Script
Initializes database and starts the FastAPI server
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Verify Python 3.9+"""
    if sys.version_info < (3, 9):
        print("[FAIL] Python 3.9+ required")
        sys.exit(1)
    print(f"[OK] Python {sys.version.split()[0]}")

def check_dependencies():
    """Check if all dependencies are installed"""
    required = ['fastapi', 'sqlalchemy', 'uvicorn', 'pydantic']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"[FAIL] Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    print("[OK] All dependencies installed")

def setup_environment():
    """Load environment variables"""
    from pathlib import Path
    
    env_file = Path('.env')
    if not env_file.exists():
        print("[WARN] .env file not found, using defaults")
        print("  Run: cp .env.example .env")
    else:
        print("[OK] Environment configured")

def initialize_database():
    """Create database tables"""
    try:
        from app.models.base import Base
        from app.database.session import engine
        
        Base.metadata.create_all(bind=engine)
        print("[OK] Database initialized")
    except Exception as e:
        print(f"[FAIL] Database initialization failed: {e}")
        sys.exit(1)

def print_startup_banner():
    """Print startup information"""
    banner = """
======================================================================
                    CrisisGrid Backend Engine                         
           Multi-Agent Crisis Response System v1.0                    
======================================================================

Starting FastAPI server...

API Available at:
   - Interactive Docs:  http://localhost:8000/docs
   - ReDoc:            http://localhost:8000/redoc
   - OpenAPI Schema:   http://localhost:8000/openapi.json

Example Workflow:
   1. POST /api/v1/simulations/          - Create simulation
   2. POST /api/v1/simulations/{id}/agents - Add agents
   3. POST /api/v1/simulations/{id}/step - Execute timestep
   4. GET  /api/v1/simulations/{id}/metrics - Get metrics

Documentation: See API_CONTRACT.md

Press Ctrl+C to stop the server.
"""
    print(banner)

def main():
    """Main startup sequence"""
    print("=" * 70)
    print("CrisisGrid Backend Engine - Startup")
    print("=" * 70)
    print()
    
    # Pre-flight checks
    print("Running pre-flight checks...")
    check_python_version()
    check_dependencies()
    setup_environment()
    initialize_database()
    
    print()
    print_startup_banner()
    
    # Start server
    try:
        subprocess.run([
            'python', '-m', 'uvicorn',
            'main:app',
            '--reload',
            '--host', '0.0.0.0',
            '--port', '8000'
        ])
    except KeyboardInterrupt:
        print("\n\n[OK] Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"[FAIL] Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
