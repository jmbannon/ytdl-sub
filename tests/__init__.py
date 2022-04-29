# Add test modules to the system path so pycharm auto-imports work
import os
import sys

PROJECT_PATH = os.getcwd()
TESTS_PATH = os.path.join(PROJECT_PATH, "tests")
sys.path.append(TESTS_PATH)
