import sys
import os
import unittest

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from validator import ValidatorEngine

class TestValidatorEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We assume the user has run the crawler and western_modules.json exists
        data_dir = os.path.dirname(os.path.dirname(__file__))
        cls.validator = ValidatorEngine(data_dir=data_dir)

    def test_normalize_course(self):
        self.assertEqual(self.validator.normalize_course("Calculus 1000A/B"), "CALCULUS 1000")
        self.assertEqual(self.validator.normalize_course("Math 1600 A/B"), "MATH 1600")
        self.assertEqual(self.validator.normalize_course("COMPSCI 1026 A"), "COMPSCI 1026")
        self.assertEqual(self.validator.normalize_course("BUSINESS ADMINISTRATION 1220E"), "BUSINESS ADMINISTRATION 1220")

    def test_check_course_match(self):
        student_courses = ["CALCULUS 1000", "MATH 1600", "COMPSCI 1026"]
        self.assertTrue(self.validator.check_course_match("Calculus 1000A/B", student_courses))
        self.assertFalse(self.validator.check_course_match("Calculus 1501A/B", student_courses))
        
if __name__ == '__main__':
    unittest.main()
