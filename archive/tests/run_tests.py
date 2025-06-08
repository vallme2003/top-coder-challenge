"""
Test runner for the reimbursement system.

This script runs all unit tests and generates a coverage report.
"""

import unittest
import sys
import os
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)  # Reduce noise during testing


def run_all_tests():
    """
    Run all unit tests and return the results.
    
    Returns:
        unittest.TestResult: Results of running all tests
    """
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    return result


def generate_coverage_report():
    """
    Generate a test coverage report if coverage.py is available.
    """
    try:
        import coverage
        
        # Start coverage measurement
        cov = coverage.Coverage()
        cov.start()
        
        # Run tests
        result = run_all_tests()
        
        # Stop coverage and generate report
        cov.stop()
        cov.save()
        
        print("\n" + "="*50)
        print("COVERAGE REPORT")
        print("="*50)
        cov.report(show_missing=True)
        
        # Generate HTML report if possible
        try:
            cov.html_report(directory='coverage_html')
            print(f"\nHTML coverage report generated in: coverage_html/index.html")
        except Exception as e:
            print(f"Could not generate HTML report: {e}")
        
        return result
        
    except ImportError:
        print("Coverage.py not available. Running tests without coverage analysis.")
        return run_all_tests()


def main():
    """Main test runner function"""
    print("Running ACME Corp Reimbursement System Tests")
    print("=" * 50)
    
    # Run tests with or without coverage
    if '--coverage' in sys.argv or '--cov' in sys.argv:
        result = generate_coverage_report()
    else:
        result = run_all_tests()
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    # Exit with appropriate code
    if result.failures or result.errors:
        print(f"\n❌ Tests FAILED")
        sys.exit(1)
    else:
        print(f"\n✅ All tests PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()