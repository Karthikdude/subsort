
#!/usr/bin/env python3
"""
Comprehensive test script for SubSort CLI tool
Tests all modules, options, and features
"""

import subprocess
import sys
import os
import time

def run_test(description, command, expected_success=True):
    """Run a test command and report results"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    try:
        start_time = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        end_time = time.time()
        
        print(f"Exit code: {result.returncode}")
        print(f"Execution time: {end_time - start_time:.2f} seconds")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout[:1000] + "..." if len(result.stdout) > 1000 else result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr)
        
        if expected_success:
            if result.returncode == 0:
                print("✅ TEST PASSED")
            else:
                print("❌ TEST FAILED")
        else:
            print("ℹ️ TEST COMPLETED")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ TEST TIMED OUT")
        return False
    except Exception as e:
        print(f"💥 TEST ERROR: {e}")
        return False

def main():
    """Run comprehensive tests"""
    print("🚀 Starting SubSort Comprehensive Testing")
    
    # Create test file
    with open('test_domains.txt', 'w') as f:
        f.write("google.com\ngithub.com\nexample.com\nhttpbin.org\n")
    
    tests = [
        # Basic functionality tests
        ("Help command", "python main.py --help"),
        ("Examples command", "python main.py --examples"),
        
        # Basic module tests
        ("Status module only", "python main.py -i test_domains.txt --status"),
        ("Server module only", "python main.py -i test_domains.txt --server"),
        ("Title module only", "python main.py -i test_domains.txt --title"),
        
        # Multiple modules
        ("Status + Server + Title", "python main.py -i test_domains.txt --status --server --title"),
        
        # Advanced modules
        ("Tech stack detection", "python main.py -i test_domains.txt --techstack"),
        ("Virtual host detection", "python main.py -i test_domains.txt --vhost"),
        ("Response time analysis", "python main.py -i test_domains.txt --responsetime"),
        ("Favicon hash", "python main.py -i test_domains.txt --faviconhash"),
        ("Robots.txt analysis", "python main.py -i test_domains.txt --robots"),
        
        # New modules
        ("JavaScript extraction", "python main.py -i test_domains.txt --js"),
        ("Authentication detection", "python main.py -i test_domains.txt --auth"),
        ("JS vulnerability scan", "python main.py -i test_domains.txt --jsvuln"),
        ("Login panels detection", "python main.py -i test_domains.txt --loginpanels"),
        ("JWT analysis", "python main.py -i test_domains.txt --jwt"),
        ("CNAME records", "python main.py -i test_domains.txt --cname"),
        
        # Output format tests
        ("JSON output", "python main.py -i test_domains.txt --status --server -o test_output.json --output-format json"),
        ("CSV output", "python main.py -i test_domains.txt --status --server -o test_output.csv --output-format csv"),
        ("TXT output", "python main.py -i test_domains.txt --status --server -o test_output.txt --output-format txt"),
        
        # New features tests
        ("Status code filtering (200)", "python main.py -i test_domains.txt --status -mc 200"),
        ("Status code filtering (404)", "python main.py -i test_domains.txt --status -mc 404"),
        ("Individual module files", "python main.py -i test_domains.txt --status --server --techstack --individual -o test_individual.txt"),
        ("Plain text output", "python main.py -i test_domains.txt --status --server --title --plain-text"),
        ("Plain text with filtering", "python main.py -i test_domains.txt --status --server -mc 200 --plain-text"),
        ("Plain text to file", "python main.py -i test_domains.txt --status --server --title --plain-text -o test_plain.txt"),
        
        # Performance tests
        ("High thread count", "python main.py -i test_domains.txt --status --threads 100 --timeout 3"),
        ("Silent mode", "python main.py -i test_domains.txt --status --silent"),
        ("Verbose mode", "python main.py -i test_domains.txt --status -v"),
        
        # Comprehensive test
        ("All modules together", "python main.py -i test_domains.txt --status --server --title --techstack --vhost --responsetime --faviconhash --robots --threads 20 --timeout 10 -v"),
        
        # Edge cases
        ("No modules specified", "python main.py -i test_domains.txt"),
        ("Non-existent file", "python main.py -i non_existent.txt --status", False),
    ]
    
    passed = 0
    total = len(tests)
    
    for description, command, *expected in tests:
        expected_success = expected[0] if expected else True
        if run_test(description, command, expected_success):
            passed += 1
    
    print(f"\n{'='*60}")
    print(f"🎯 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    # Check if output files were created
    print(f"\n📁 OUTPUT FILES CHECK:")
    output_files = ['test_output.json', 'test_output.csv', 'test_output.txt', 'test_plain.txt', 'test_individual.txt']
    for file in output_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size} bytes)")
        else:
            print(f"❌ {file} (missing)")
    
    # Check for individual module files
    if os.path.exists('test_individual_modules'):
        module_files = os.listdir('test_individual_modules')
        print(f"📂 Individual module files: {len(module_files)} files")
        for mfile in module_files:
            print(f"   - {mfile}")
    
    # Cleanup
    cleanup_files = ['test_domains.txt'] + output_files
    for file in cleanup_files:
        if os.path.exists(file):
            os.remove(file)
    
    if os.path.exists('test_individual_modules'):
        import shutil
        shutil.rmtree('test_individual_modules')
    
    print(f"\n🧹 Cleanup completed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
