import sys
import os
import unittest

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from validator import ValidatorEngine

class TestValidatorEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_dir = os.path.dirname(os.path.dirname(__file__))
        cls.validator = ValidatorEngine(data_dir=data_dir)

    def test_normalize_course(self):
        # Full names stay as-is
        self.assertEqual(self.validator.normalize_course("Calculus 1000A/B"), "CALCULUS 1000")
        self.assertEqual(self.validator.normalize_course("BUSINESS ADMINISTRATION 1220E"), "BUSINESS ADMINISTRATION 1220")
        # Abbreviations get resolved to full names
        self.assertEqual(self.validator.normalize_course("COMPSCI 1026A"), "COMPUTER SCIENCE 1026")
        self.assertEqual(self.validator.normalize_course("MATH 1600A/B"), "MATHEMATICS 1600")
        self.assertEqual(self.validator.normalize_course("ECON 1021A/B"), "ECONOMICS 1021")

    def test_check_course_match(self):
        # Student types abbreviations, module data has full names — should match
        student_courses_norm = [
            self.validator.normalize_course(c) for c in 
            ["COMPSCI 2208A", "MATH 1600A", "CALCULUS 1000A"]
        ]
        self.assertTrue(self.validator.check_course_match("Computer Science 2208A/B", student_courses_norm))
        self.assertTrue(self.validator.check_course_match("Mathematics 1600A/B", student_courses_norm))
        self.assertTrue(self.validator.check_course_match("Calculus 1000A/B", student_courses_norm))
        self.assertFalse(self.validator.check_course_match("Calculus 1501A/B", student_courses_norm))

    def test_evaluate_compsci_major(self):
        # Module 21112 = MAJOR IN COMPUTER SCIENCE
        # COMPSCI 2208A and 2209B are required courses in the first group (3.5 credits)
        result = self.validator.evaluate("21112", ["COMPSCI 2208A", "COMPSCI 2209B"])
        self.assertGreater(result["progress_percentage"], 0)
        self.assertGreater(result["total_credits_met"], 0)
        # Should have found at least 2 courses matching
        all_met = []
        for g in result["groups"]:
            all_met.extend(g.get("courses_met", []))
        self.assertGreaterEqual(len(all_met), 2)
        
if __name__ == '__main__':
    unittest.main()
