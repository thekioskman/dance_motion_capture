import unittest

# Discover and run all the tests in the 'tests' directory
def run_all_tests():
    # Discover all test files in the 'tests' folder
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')  # Finds all test_*.py files in the tests folder
    
    # Run the test suite
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    run_all_tests()