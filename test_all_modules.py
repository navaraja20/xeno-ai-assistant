"""
Comprehensive test script for XENO AI Assistant.
Tests all automation modules to verify they work correctly.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def test_imports():
    """Test that all modules can be imported."""
    print_header("Testing Module Imports")
    
    modules = [
        "modules.email_handler",
        "modules.github_manager",
        "modules.job_automation",
        "modules.linkedin_automation",
        "modules.calendar_sync",
        "modules.oauth_helper",
        "modules.ai_chat"
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            return False
    
    return True

def test_job_automation():
    """Test job automation module (doesn't require credentials)."""
    print_header("Testing Job Automation")
    
    try:
        from modules.job_automation import JobAutomation
        
        job_auto = JobAutomation()
        print("✓ JobAutomation initialized")
        
        # Test job search (may fail due to web scraping, but should not crash)
        print("  Testing job search...")
        jobs = job_auto.search_indeed("Python Developer", "", max_results=5)
        print(f"  Found {len(jobs)} jobs on Indeed")
        
        if jobs:
            print(f"  Sample job: {jobs[0]['title']} at {jobs[0]['company']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Job automation test failed: {e}")
        return False

def test_oauth_helper():
    """Test OAuth helper module."""
    print_header("Testing OAuth Helper")
    
    try:
        from modules.oauth_helper import OAuthHelper
        
        oauth = OAuthHelper(redirect_port=8080)
        print("✓ OAuthHelper initialized")
        
        # Test instruction methods
        github_instructions = OAuthHelper.get_github_token_instructions()
        google_instructions = OAuthHelper.get_google_app_password_instructions()
        
        print("✓ GitHub instructions available")
        print("✓ Google instructions available")
        
        return True
        
    except Exception as e:
        print(f"✗ OAuth helper test failed: {e}")
        return False

def test_database():
    """Test database models."""
    print_header("Testing Database")
    
    try:
        from models.database import (
            init_db, ConversationHistory, JobApplication,
            GitHubRepository, Task
        )
        
        # Initialize database
        init_db()
        print("✓ Database initialized")
        
        # Test that models are properly defined
        print("✓ ConversationHistory model defined")
        print("✓ JobApplication model defined")
        print("✓ GitHubRepository model defined")
        print("✓ Task model defined")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration loading."""
    print_header("Testing Configuration")
    
    try:
        from core.config import load_config
        
        config = load_config()
        print(f"✓ Configuration loaded")
        print(f"  User: {config.user_name}")
        print(f"  AI API Key: {'Set' if config.ai.api_key else 'Not set'}")
        print(f"  Email: {'Configured' if config.email and config.email.address else 'Not configured'}")
        print(f"  GitHub: {'Configured' if config.github and config.github.username else 'Not configured'}")
        print(f"  LinkedIn: {'Configured' if config.linkedin and config.linkedin.email else 'Not configured'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_ui_components():
    """Test that UI components can be imported."""
    print_header("Testing UI Components")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.setup_wizard import SetupWizard
        from ui.tray import XenoTrayIcon
        
        print("✓ SetupWizard can be imported")
        print("✓ XenoTrayIcon can be imported")
        print("✓ All UI components available")
        
        return True
        
    except Exception as e:
        print(f"✗ UI components test failed: {e}")
        return False

def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("  XENO AI ASSISTANT - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Job Automation", test_job_automation),
        ("OAuth Helper", test_oauth_helper),
        ("UI Components", test_ui_components),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} crashed: {e}")
            results.append((name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} | {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! XENO is ready to go!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
