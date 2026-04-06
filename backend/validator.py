import json
import os
import re
from typing import List, Dict, Any

class ValidatorEngine:
    def __init__(self, data_dir: str):
        self.modules_path = os.path.join(data_dir, "western_modules.json")
        self.courses_path = os.path.join(data_dir, "western_courses.json")
        self.modules_data = self._load_json(self.modules_path)
        self.courses_data = self._load_json(self.courses_path)
        
    def _load_json(self, path: str) -> Dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return {}
            
    def normalize_course(self, course_str: str) -> str:
        """
        Normalize a course string to standard format. e.g. 'Calculus 1000A/B' -> 'CALCULUS 1000'
        """
        if not course_str:
            return ""
        course_str = str(course_str).upper().strip()
        match = re.search(r'([A-Z\s\-]+?)\s*(\d{4})', course_str)
        if match:
            subject = match.group(1).strip()
            num = match.group(2)
            return f"{subject} {num}"
        return course_str

    def check_course_match(self, required_str: str, student_courses_normalized: List[str]) -> bool:
        """Check if required_str (e.g. 'Calculus 1000A/B') is satisfied by student courses"""
        normalized_req = self.normalize_course(required_str)
        return normalized_req in student_courses_normalized

    def evaluate(self, module_id: str, student_courses: List[str]) -> Dict[str, Any]:
        module = self.modules_data.get('modules', {}).get(module_id)
        if not module:
            return {"error": "Module not found"}
            
        student_courses_norm = [self.normalize_course(c) for c in student_courses]
        
        result = {
            "module_id": module_id,
            "module_name": module.get("name"),
            "module_type": module.get("type"),
            "faculty": module.get("faculty"),
            "department": module.get("department"),
            "total_courses_required": module.get("total_courses", 0),
            "groups": []
        }
        
        total_credits_met = 0.0
        total_credits_required = 0.0
        
        for group in module.get("course_groups", []):
            group_type = group.get("type")
            credits_required = float(group.get("credits", 0))
            total_credits_required += credits_required
            
            group_res = {
                "type": group_type,
                "credits_required": credits_required,
                "credits_met": 0.0,
                "is_met": False,
                "courses_met": [],
                "courses_missing": []
            }
            
            if group_type == "required":
                # Must take these exact courses
                for course in group.get("courses", []):
                    course_name = course.get("name")
                    if self.check_course_match(course_name, student_courses_norm):
                        group_res["courses_met"].append(course_name)
                    else:
                        group_res["courses_missing"].append(course_name)
                
                # Calculate credits met for required
                # Assume each required course contributes to the pool equally if not otherwise specified
                courses_len = len(group.get("courses", []))
                if courses_len > 0:
                    proportion = len(group_res["courses_met"]) / courses_len
                    group_res["credits_met"] = round(credits_required * proportion, 2)
                    group_res["is_met"] = len(group_res["courses_missing"]) == 0
                    
            elif group_type == "choose_from":
                # Need to pick certain credits from a list
                courses_list = group.get("courses", [])
                credits_found = 0.0
                for course in courses_list:
                    course_name = course.get("name")
                    if self.check_course_match(course_name, student_courses_norm):
                        course_weigh = self._get_course_weight(course_name)
                        credits_found += course_weigh
                        group_res["courses_met"].append(course_name)
                        
                    if credits_found >= credits_required:
                        break
                        
                group_res["credits_met"] = round(min(credits_found, credits_required), 2)
                group_res["is_met"] = group_res["credits_met"] >= credits_required
                
                # For choose_from, you are missing options if you haven't met the credit mark
                if not group_res["is_met"]:
                    group_res["courses_missing"] = [c.get("name") for c in courses_list if c.get("name") not in group_res["courses_met"]]
                
            elif group_type == "additional":
                group_res["is_met"] = False
                group_res["description"] = group.get("description")
                group_res["notes"] = "Manual check required for unstructured text"
                
            total_credits_met += group_res["credits_met"]
            result["groups"].append(group_res)
            
        result["total_credits_met"] = round(total_credits_met, 2)
        result["total_credits_required"] = round(total_credits_required, 2)
        result["progress_percentage"] = round((total_credits_met / total_credits_required * 100), 2) if total_credits_required > 0 else 0.0
        
        return result

    def _get_course_weight(self, course_name: str) -> float:
        # Look up weight in courses_data
        norm_name = self.normalize_course(course_name)
        for c_data in self.courses_data.get("courses", {}).values():
            if self.normalize_course(c_data.get("course_title", "")) == norm_name:
                w = c_data.get("course_weight")
                try:
                    return float(w) if w else 0.5
                except:
                    return 0.5
        # Default to half credit
        return 0.5
