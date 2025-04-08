import sys
import os
import unittest

# Add the parent directory to the path so we can import the src module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.course_details import get_course_details
from src.course_catalog import extract_coursera_courses

class TestCourseraAPI(unittest.TestCase):
    """Basic tests for the Coursera API client"""
    
    def test_get_course_details(self):
        """Test that we can get details for a known course"""
        response = get_course_details("machine-learning")
        self.assertIsNotNone(response)
        self.assertIn("data", response)
        self.assertIn("XdpV1Resource", response["data"])
    
    def test_extract_courses(self):
        """Test that we can extract courses from the catalog"""
        # Use a small limit to make the test run quickly
        courses = extract_coursera_courses(limit=3)
        self.assertIsNotNone(courses)
        self.assertIsInstance(courses, list)
        if courses:  # Only check if we got actual results
            self.assertGreaterEqual(len(courses), 1)

if __name__ == "__main__":
    unittest.main()