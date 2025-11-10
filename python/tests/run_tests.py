#!/usr/bin/env python3
"""
Test runner for Vectro+ Python API.

This script runs the comprehensive test suite and provides detailed
reporting on the Python bindings functionality.
"""

import sys
import os
import unittest
import time
from pathlib import Path

# Add the python package to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_tests():
    """Run the Vectro+ test suite with detailed reporting."""
    
    print("="*60)
    print(" Vectro+ Python API Test Suite")
    print("="*60)
    print()
    
    # Check if Rust extension is available
    try:
        import vectro_plus as vp
        rust_available = True
        print("✅ Rust extension loaded successfully")
        print(f"   Version: {vp.version()}")
        print(f"   Author: {vp.__author__}")
    except ImportError as e:
        rust_available = False
        print(f"❌ Rust extension not available: {e}")
        print("   Some tests will be skipped")
    
    print()
    print("-"*40)
    print(" Running Tests")
    print("-"*40)
    
    # Discover and run tests
    start_time = time.time()
    
    test_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    end_time = time.time()
    
    # Print summary
    print()
    print("-"*40)
    print(" Test Summary")
    print("-"*40)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total_tests - failures - errors - skipped
    
    print(f"Time Elapsed: {end_time - start_time:.2f} seconds")
    print(f"Tests Run: {total_tests}")
    print(f"  ✅ Passed: {passed}")
    if failures > 0:
        print(f"  ❌ Failed: {failures}")
    if errors > 0:
        print(f"  💥 Errors: {errors}")
    if skipped > 0:
        print(f"  ⏭️  Skipped: {skipped}")
    
    print()
    
    if failures == 0 and errors == 0:
        print("🎉 All tests passed! Python API is ready for use.")
        success = True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        success = False
    
    # Print next steps
    print()
    print("-"*40)
    print(" Next Steps")
    print("-"*40)
    
    if rust_available and success:
        print("1. The Python API is working correctly")
        print("2. Try the example scripts in examples/")
        print("3. Install with: pip install -e .")
        print("4. Import with: import vectro_plus as vp")
    elif not rust_available:
        print("1. Build the Rust extension:")
        print("   cargo build --release -p vectro_py")
        print("2. Install Python package:")
        print("   pip install -e .")
        print("3. Re-run tests")
    else:
        print("1. Fix the failing tests")
        print("2. Re-run the test suite")
        print("3. Check the Rust extension build")
    
    return success


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)