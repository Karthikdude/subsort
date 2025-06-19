
#!/usr/bin/env python3
"""
Comprehensive test script for SubSort - tests all modules and functionality
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_test(name, cmd, expected_keywords=None, check_files=None, timeout=120):
    """Run a single test command"""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"COMMAND: {' '.join(cmd)}")
    print(f"{'='*80}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print(f"EXIT CODE: {result.returncode}")

        # Check for expected keywords if provided
        success = True
        if expected_keywords:
            found_keywords = []
            output_text = result.stdout.lower() + result.stderr.lower()
            for keyword in expected_keywords:
                if keyword.lower() in output_text:
                    found_keywords.append(keyword)

            print(f"EXPECTED KEYWORDS: {expected_keywords}")
            print(f"FOUND KEYWORDS: {found_keywords}")

        # Check for file creation if specified
        if check_files:
            for file_path in check_files:
                if os.path.exists(file_path):
                    print(f"✅ File created: {file_path}")
                    # Check file size
                    size = os.path.getsize(file_path)
                    print(f"   File size: {size} bytes")
                else:
                    print(f"❌ File not created: {file_path}")
                    success = False

        # Check for critical errors
        critical_errors = ['attributeerror', 'syntaxerror', 'importerror', 'modulenotfounderror']
        error_text = result.stderr.lower()
        for error in critical_errors:
            if error in error_text:
                print(f"❌ Critical error detected: {error}")
                success = False

        if result.returncode == 0 and success:
            print("✅ TEST PASSED")
            return True
        else:
            print("❌ TEST FAILED")
            return False

    except subprocess.TimeoutExpired:
        print("❌ TEST FAILED - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ TEST FAILED - EXCEPTION: {e}")
        return False

def create_test_files():
    """Create test files for comprehensive testing"""
    # Basic test file
    test_domains = [
        "google.com",
        "github.com", 
        "stackoverflow.com",
        "httpbin.org",
        "example.com",
        "news.ycombinator.com",
        "reddit.com",
        "twitter.com"
    ]
    
    with open("test_subdomains.txt", 'w') as f:
        f.write('\n'.join(test_domains))
    
    # Small test file for quick tests
    with open("test_small.txt", 'w') as f:
        f.write("google.com\nexample.com\nhttpbin.org\n")

def main():
    """Run comprehensive tests"""
    print("SubSort Comprehensive Test Suite - All Modules")
    print("=" * 80)

    # Ensure test files exist
    create_test_files()

    # Test cases covering all functionality
    tests = [
        {
            "name": "01 - Help Command",
            "cmd": ["python", "main.py", "--help"],
            "expected": ["SubSort", "Options", "Enhanced CLI"],
            "timeout": 30
        },
        {
            "name": "02 - Basic Status Check",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--status", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 45
        },
        {
            "name": "03 - Status + Server Modules", 
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--status", "--server", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 60
        },
        {
            "name": "04 - Status + Title Modules",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--status", "--title", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 60
        },
        {
            "name": "05 - Core Modules (Status + Server + Title)",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--status", "--server", "--title", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 75
        },
        {
            "name": "06 - Tech Stack Detection",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--techstack", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 60
        },
        {
            "name": "07 - Virtual Host Detection",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--vhost", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 60
        },
        {
            "name": "08 - Response Time Analysis",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--responsetime", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 60
        },
        {
            "name": "09 - Favicon Hash Generation",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--faviconhash", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 60
        },
        {
            "name": "10 - Robots.txt Analysis",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--robots", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 60
        },
        {
            "name": "11 - JavaScript Extraction",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--js", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 60
        },
        {
            "name": "12 - Authentication Detection",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--auth", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 60
        },
        {
            "name": "13 - Output to File (TXT)",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--status", "--server", "-o", "test_output.txt", "--silent", "--timeout", "15"],
            "expected": [],
            "check_files": ["test_output.txt"],
            "timeout": 60
        },
        {
            "name": "14 - Output to JSON",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--status", "--server", "-o", "test_output.json", "--output-format", "json", "--silent", "--timeout", "15"],
            "expected": [],
            "check_files": ["test_output.json"],
            "timeout": 60
        },
        {
            "name": "15 - Individual Module Files",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--status", "--server", "--individual", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 60
        },
        {
            "name": "16 - Status Code Filtering",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--status", "-mc", "200", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 60
        },
        {
            "name": "17 - Plain Text Output",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--status", "--plain-text", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 60
        },
        {
            "name": "18 - High Thread Count",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--status", "--threads", "20", "--silent", "--timeout", "15"],
            "expected": [],
            "timeout": 60
        },
        {
            "name": "19 - All Advanced Modules",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--techstack", "--vhost", "--responsetime", "--faviconhash", "--robots", "--silent", "--timeout", "20"],
            "expected": [],
            "timeout": 90
        },
        {
            "name": "20 - Full Module Suite",
            "cmd": ["python", "main.py", "-i", "test_small.txt", "--status", "--server", "--title", "--techstack", "--vhost", "--responsetime", "--faviconhash", "--robots", "--js", "--auth", "--silent", "--timeout", "25"],
            "expected": [],
            "timeout": 120
        }
    ]

    passed = 0
    failed = 0
    start_time = time.time()

    for i, test in enumerate(tests, 1):
        print(f"\nRunning test {i}/{len(tests)}...")
        success = run_test(
            test["name"],
            test["cmd"],
            test.get("expected"),
            test.get("check_files"),
            test.get("timeout", 60)
        )

        if success:
            passed += 1
        else:
            failed += 1

        # Add small delay between tests
        time.sleep(1)

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\n{'='*80}")
    print("COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*80}")
    print(f"TOTAL TESTS: {passed + failed}")
    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print(f"SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")
    print(f"TOTAL TIME: {total_time:.1f} seconds")
    print(f"AVERAGE TIME PER TEST: {total_time/(passed+failed):.1f} seconds")

    # Clean up test files
    test_files = [
        "test_subdomains.txt", "test_small.txt", "test_output.txt", 
        "test_output.json", "test_output.csv"
    ]
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Cleaned up: {file_path}")
            except:
                pass

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ SubSort is working correctly with all modules!")
        sys.exit(0)
    else:
        print(f"\n❌ {failed} TESTS FAILED!")
        print("🔧 Please check the failed tests above for issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()
