#!/usr/bin/env python3
"""
Kronos Test Runner

A comprehensive test runner for all Kronos tests organized by functionality.
Runs all tests in the appropriate order and provides detailed reporting.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --category chat    # Run only chat tests
    python run_tests.py --category logs    # Run only log tests
    python run_tests.py --category search  # Run only search tests
    python run_tests.py --category sync    # Run only sync tests
    python run_tests.py --category integration  # Run only integration tests
    python run_tests.py --list            # List all available tests
"""

import sys
import os
import importlib.util
import argparse
from pathlib import Path

def get_test_files(test_dir):
    """Get all test files in a directory."""
    test_path = Path(test_dir)
    if not test_path.exists():
        return []
    
    return [f for f in test_path.glob("test_*.py") if f.is_file()]

def run_test_file(test_file):
    """Run a single test file."""
    print(f"\n{'='*60}")
    print(f"Running: {test_file.name}")
    print(f"{'='*60}")
    
    try:
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location("test_module", test_file)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        
        # Find the main test function (usually the function that starts with test_)
        test_functions = [attr for attr in dir(test_module) 
                         if callable(getattr(test_module, attr)) and 
                         (attr.startswith('test_') or attr == 'main')]
        
        if test_functions:
            # Run the first test function found
            test_func = getattr(test_module, test_functions[0])
            test_func()
            print(f"✅ {test_file.name} - PASSED")
            return True
        else:
            print(f"⚠️  {test_file.name} - NO TEST FUNCTION FOUND")
            return False
            
    except Exception as e:
        print(f"❌ {test_file.name} - FAILED: {str(e)}")
        return False

def run_tests_in_category(category_path, category_name):
    """Run all tests in a specific category."""
    test_files = get_test_files(category_path)
    
    if not test_files:
        print(f"No tests found in {category_name}")
        return 0, 0
    
    print(f"\n🔍 Running {category_name.upper()} tests...")
    passed = 0
    total = len(test_files)
    
    for test_file in sorted(test_files):
        if run_test_file(test_file):
            passed += 1
    
    print(f"\n📊 {category_name.upper()} Results: {passed}/{total} tests passed")
    return passed, total

def list_tests():
    """List all available tests."""
    test_base = Path(__file__).parent
    categories = ['chat', 'logs', 'search', 'sync', 'integration']
    
    print("Available tests by category:\n")
    
    for category in categories:
        category_path = test_base / category
        test_files = get_test_files(category_path)
        
        print(f"📁 {category.upper()}:")
        if test_files:
            for test_file in sorted(test_files):
                print(f"   - {test_file.name}")
        else:
            print(f"   (no tests)")
        print()

def main():
    parser = argparse.ArgumentParser(description='Kronos Test Runner')
    parser.add_argument('--category', choices=['chat', 'logs', 'search', 'sync', 'integration'], 
                       help='Run tests for a specific category only')
    parser.add_argument('--list', action='store_true', help='List all available tests')
    
    args = parser.parse_args()
    
    if args.list:
        list_tests()
        return
    
    test_base = Path(__file__).parent
    
    print("🚀 Kronos Test Suite")
    print("=" * 50)
    
    total_passed = 0
    total_tests = 0
    
    if args.category:
        # Run tests for specific category
        category_path = test_base / args.category
        passed, total = run_tests_in_category(category_path, args.category)
        total_passed += passed
        total_tests += total
    else:
        # Run all tests in order
        categories = [
            ('sync', 'Sync & Database'),
            ('logs', 'Logging'),
            ('search', 'Search & Knowledge Base'),
            ('chat', 'Chat & Conversations'),
            ('integration', 'Integration Tests')
        ]
        
        for category, display_name in categories:
            category_path = test_base / category
            passed, total = run_tests_in_category(category_path, display_name)
            total_passed += passed
            total_tests += total
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"🏁 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_tests - total_passed}")
    
    if total_passed == total_tests:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"💥 {total_tests - total_passed} test(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    # Add the src directory to Python path
    src_path = Path(__file__).parent.parent
    sys.path.insert(0, str(src_path))
    
    main()
