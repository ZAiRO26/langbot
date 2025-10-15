#!/usr/bin/env python3
"""
LinkedIn Automation Agent - System Test

This script tests all components of the LinkedIn automation system
to ensure everything is properly configured and working.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List

# Test imports
def test_imports():
    """Test that all required modules can be imported"""
    
    print("Testing imports...")
    
    try:
        import config
        print("✓ config module imported")
        
        import linkedin_client
        print("✓ linkedin_client module imported")
        
        import perplexity_client
        print("✓ perplexity_client module imported")
        
        import engagement_manager
        print("✓ engagement_manager module imported")
        
        import scheduler
        print("✓ scheduler module imported")
        
        import logger_config
        print("✓ logger_config module imported")
        
        import topics_config
        print("✓ topics_config module imported")
        
        import main
        print("✓ main module imported")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_configuration():
    """Test configuration setup"""
    
    print("\nTesting configuration...")
    
    try:
        from config import settings, validate_config
        
        # Check if .env file exists
        if not os.path.exists('.env'):
            print("✗ .env file not found")
            print("  Please copy .env.example to .env and configure your API keys")
            return False
        
        print("✓ .env file found")
        
        # Test configuration validation
        try:
            validate_config()
            print("✓ Configuration validation passed")
        except ValueError as e:
            print(f"✗ Configuration validation failed: {e}")
            return False
        
        # Check topics
        if settings.weekly_topics:
            print(f"✓ Weekly topics configured ({len(settings.weekly_topics)} topics)")
            for i, topic in enumerate(settings.weekly_topics[:3], 1):
                print(f"    {i}. {topic}")
            if len(settings.weekly_topics) > 3:
                print(f"    ... and {len(settings.weekly_topics) - 3} more")
        else:
            print("⚠ No weekly topics configured")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_topics_manager():
    """Test topics configuration system"""
    
    print("\nTesting topics manager...")
    
    try:
        from topics_config import topics_manager, get_current_topics
        
        # Test getting current topics
        topics = get_current_topics()
        print(f"✓ Topics manager working ({len(topics)} topics loaded)")
        
        # Test status
        status = topics_manager.get_status()
        print(f"✓ Current week: {status['current_week']}")
        print(f"✓ Auto-rotate: {status['auto_rotate']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Topics manager test failed: {e}")
        return False

async def test_linkedin_client():
    """Test LinkedIn client functionality"""
    
    print("\nTesting LinkedIn client...")
    
    try:
        from linkedin_client import LinkedInClient
        
        client = LinkedInClient()
        print("✓ LinkedIn client initialized")
        
        # Test rate limiter
        if hasattr(client, 'rate_limiter'):
            print("✓ Rate limiter configured")
        
        # Note: We don't test actual API calls to avoid rate limits
        print("✓ LinkedIn client ready (API calls not tested to avoid rate limits)")
        
        return True
        
    except Exception as e:
        print(f"✗ LinkedIn client test failed: {e}")
        return False

async def test_perplexity_client():
    """Test Perplexity AI client functionality"""
    
    print("\nTesting Perplexity AI client...")
    
    try:
        from perplexity_client import PerplexityClient
        
        client = PerplexityClient()
        print("✓ Perplexity client initialized")
        
        # Test rate limiter
        if hasattr(client, 'rate_limiter'):
            print("✓ Rate limiter configured")
        
        # Note: We don't test actual API calls to avoid costs
        print("✓ Perplexity client ready (API calls not tested to avoid costs)")
        
        return True
        
    except Exception as e:
        print(f"✗ Perplexity client test failed: {e}")
        return False

def test_scheduler():
    """Test scheduling system"""
    
    print("\nTesting scheduler...")
    
    try:
        from scheduler import LinkedInScheduler
        
        scheduler = LinkedInScheduler()
        print("✓ Scheduler initialized")
        
        # Test scheduling logic
        next_run = scheduler.get_next_run_time()
        if next_run:
            print(f"✓ Next scheduled run: {next_run}")
        else:
            print("⚠ No next run scheduled (this is normal if not started)")
        
        return True
        
    except Exception as e:
        print(f"✗ Scheduler test failed: {e}")
        return False

def test_logging():
    """Test logging system"""
    
    print("\nTesting logging system...")
    
    try:
        from logger_config import automation_logger, log_activity, log_error
        
        # Test basic logging
        automation_logger.logger.info("Test log message")
        print("✓ Basic logging working")
        
        # Test activity logging
        log_activity("test_activity", {"test": True}, success=True)
        print("✓ Activity logging working")
        
        # Test error logging
        log_error("test_error", "This is a test error")
        print("✓ Error logging working")
        
        # Check log directory
        if os.path.exists('logs'):
            print("✓ Logs directory exists")
            
            log_files = ['activity.log', 'error.log', 'performance.log']
            for log_file in log_files:
                if os.path.exists(f'logs/{log_file}'):
                    print(f"✓ {log_file} exists")
                else:
                    print(f"⚠ {log_file} not found (will be created when needed)")
        else:
            print("⚠ Logs directory not found (will be created when needed)")
        
        return True
        
    except Exception as e:
        print(f"✗ Logging test failed: {e}")
        return False

async def test_engagement_manager():
    """Test engagement manager"""
    
    print("\nTesting engagement manager...")
    
    try:
        from engagement_manager import EngagementManager
        from linkedin_client import LinkedInClient
        from perplexity_client import PerplexityClient
        
        linkedin_client = LinkedInClient()
        perplexity_client = PerplexityClient()
        
        manager = EngagementManager(linkedin_client, perplexity_client)
        print("✓ Engagement manager initialized")
        
        # Test stats
        stats = manager.get_engagement_stats()
        print("✓ Engagement stats accessible")
        
        return True
        
    except Exception as e:
        print(f"✗ Engagement manager test failed: {e}")
        return False

async def test_main_orchestrator():
    """Test main orchestrator"""
    
    print("\nTesting main orchestrator...")
    
    try:
        from main import LinkedInAutomationAgent
        
        agent = LinkedInAutomationAgent()
        print("✓ Main agent initialized")
        
        # Test status method
        status = agent.get_status()
        print("✓ Status method working")
        print(f"  Running: {status.get('is_running', False)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Main orchestrator test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are installed"""
    
    print("\nTesting dependencies...")
    
    required_packages = [
        'requests',
        'schedule',
        'python-dotenv',
        'asyncio-throttle',
        'pytz'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} not installed")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def print_system_info():
    """Print system information"""
    
    print("\n" + "="*60)
    print("SYSTEM INFORMATION")
    print("="*60)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current time: {datetime.now()}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check environment
    if os.path.exists('.env'):
        print("Environment file: ✓ Found")
    else:
        print("Environment file: ✗ Not found")
    
    # Check topics configuration
    try:
        from topics_config import topics_manager
        status = topics_manager.get_status()
        print(f"Topics configured: {status['topics_count']} topics")
        print(f"Current week: {status['current_week']}")
    except:
        print("Topics configuration: ✗ Error loading")

async def run_all_tests():
    """Run all system tests"""
    
    print("LinkedIn Automation Agent - System Test")
    print("="*60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Topics Manager", test_topics_manager),
        ("LinkedIn Client", test_linkedin_client),
        ("Perplexity Client", test_perplexity_client),
        ("Scheduler", test_scheduler),
        ("Logging", test_logging),
        ("Engagement Manager", test_engagement_manager),
        ("Main Orchestrator", test_main_orchestrator)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            results[test_name] = result
            
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your system is ready to run.")
        print("\nTo start the agent:")
        print("  python main.py")
        print("\nTo manage topics:")
        print("  python topics_config.py list")
        print("  python topics_config.py set 'Topic 1' 'Topic 2' 'Topic 3'")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please fix the issues before running the agent.")
        
        if not results.get("Dependencies", True):
            print("\n1. Install missing dependencies:")
            print("   pip install -r requirements.txt")
        
        if not results.get("Configuration", True):
            print("\n2. Configure your environment:")
            print("   cp .env.example .env")
            print("   # Edit .env with your API keys")
        
        if not results.get("Topics Manager", True):
            print("\n3. Set up your topics:")
            print("   python topics_config.py set 'Your Topic 1' 'Your Topic 2'")
    
    print_system_info()
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error during testing: {e}")
        sys.exit(1)