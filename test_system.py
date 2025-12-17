#!/usr/bin/env python3
"""
Quick test script to verify 24H alert system is working
Tests each component independently
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def test_environment():
    """Test environment variables are configured"""
    print("\n" + "="*60)
    print("✅ TEST 1: Environment Variables")
    print("="*60)
    
    required_vars = [
        "GEOEDGE_API_KEY",
        "MYSQL_HOST",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "MYSQL_DB",
        "ALERT_EMAIL",
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var, "").strip()
        if not value:
            missing.append(var)
            print(f"❌ {var}: NOT SET")
        else:
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {display_value}")
    
    if missing:
        print(f"\n⚠️ Missing: {', '.join(missing)}")
        print("→ Copy .env.example to .env and fill in your credentials")
        return False
    
    return True


def test_dependencies():
    """Test required packages are installed"""
    print("\n" + "="*60)
    print("✅ TEST 2: Python Dependencies")
    print("="*60)
    
    packages = {
        "requests": "requests",
        "pymysql": "pymysql",
        "dotenv": "dotenv",
    }
    
    missing = []
    for name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✅ {name}: installed")
        except ImportError:
            missing.append(name)
            print(f"❌ {name}: NOT installed")
    
    if missing:
        print(f"\n⚠️ Missing packages: {', '.join(missing)}")
        print(f"→ Run: pip install -r requirements.txt")
        return False
    
    return True


def test_modules():
    """Test local modules can be imported"""
    print("\n" + "="*60)
    print("✅ TEST 3: Local Modules")
    print("="*60)
    
    try:
        import config
        print("✅ config.py: OK")
    except Exception as e:
        print(f"❌ config.py: {str(e)}")
        return False
    
    try:
        import send_email
        print("✅ send_email.py: OK")
    except Exception as e:
        print(f"❌ send_email.py: {str(e)}")
        return False
    
    try:
        import main
        print("✅ main.py: OK")
    except Exception as e:
        print(f"❌ main.py: {str(e)}")
        return False
    
    return True


def test_files():
    """Test required files exist"""
    print("\n" + "="*60)
    print("✅ TEST 4: Required Files")
    print("="*60)
    
    files = [
        ".env",
        "config.py",
        "main.py",
        "send_email.py",
        "requirements.txt",
        "seen_lp_alerts.json",
    ]
    
    missing = []
    for file in files:
        if os.path.exists(file):
            print(f"✅ {file}: exists")
        else:
            missing.append(file)
            print(f"❌ {file}: NOT FOUND")
    
    if missing:
        print(f"\n⚠️ Missing files: {', '.join(missing)}")
        return False
    
    return True


def test_seen_file():
    """Test seen_lp_alerts.json is valid JSON"""
    print("\n" + "="*60)
    print("✅ TEST 5: Deduplication File")
    print("="*60)
    
    try:
        with open("seen_lp_alerts.json", "r") as f:
            seen = json.load(f)
        
        print(f"✅ seen_lp_alerts.json: valid JSON")
        print(f"   Total seen alerts: {len(seen)}")
        
        if seen:
            print(f"   Sample: {seen[0]}")
        
        return True
    except Exception as e:
        print(f"❌ seen_lp_alerts.json: {str(e)}")
        return False


def test_config():
    """Test configuration values"""
    print("\n" + "="*60)
    print("✅ TEST 6: Configuration")
    print("="*60)
    
    try:
        from config import (
            ENGLISH_COUNTRIES, LATAM_COUNTRIES, 
            GREATER_CHINA_COUNTRIES, TARGET_REGIONS,
            ALERT_CHECK_HOURS
        )
        
        print(f"✅ English countries: {len(ENGLISH_COUNTRIES)}")
        print(f"✅ LATAM countries: {len(LATAM_COUNTRIES)}")
        print(f"✅ Greater China countries: {len(GREATER_CHINA_COUNTRIES)}")
        print(f"✅ Target regions: {len(TARGET_REGIONS)}")
        print(f"✅ Alert check hours: {ALERT_CHECK_HOURS}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("🧪 LP ALERTS 24H - SYSTEM CHECK")
    print("=" * 60)
    
    tests = [
        ("Environment", test_environment),
        ("Dependencies", test_dependencies),
        ("Modules", test_modules),
        ("Files", test_files),
        ("Deduplication", test_seen_file),
        ("Configuration", test_config),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! System is ready to use.")
        print("\n📋 Next steps:")
        print("1. Review .env file has correct credentials")
        print("2. Run: python main.py")
        print("3. Check alert_checker.log for execution details")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Fix issues above before running.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
