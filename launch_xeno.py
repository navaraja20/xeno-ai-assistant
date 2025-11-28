"""
Quick Launch Script for XENO
Launch the integrated application with all features
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("  XENO v2.0 - Integrated AI Assistant")
print("=" * 60)
print()
print("Features:")
print("  ✅ AI Agent (Ollama + Gemini)")
print("  ✅ Job Hunter with Resume Tailoring")
print("  ✅ Gmail Integration")
print("  ✅ GitHub Management")
print("  ✅ Calendar Sync")
print()
print("Starting XENO...")
print("=" * 60)
print()

# Import and run
from src.jarvis import main

if __name__ == "__main__":
    sys.exit(main())
