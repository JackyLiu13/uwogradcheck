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
        self.abbrev_map = self._build_abbreviation_map()
        
    def _load_json(self, path: str) -> Dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return {}

    def _build_abbreviation_map(self) -> Dict[str, str]:
        """
        Build a bidirectional map between subject abbreviations (e.g. COMPSCI)
        and full names (e.g. COMPUTER SCIENCE) using the scraped course data.
        Both directions map to the FULL NAME as the canonical form.
        """
        # Hardcoded map of common UWO abbreviations to full subject names
        KNOWN_ABBREVIATIONS = {
            "ACTURSCI": "ACTUARIAL SCIENCE",
            "AMERSTUD": "AMERICAN STUDIES",
            "ADS": "ANALYTICS AND DECISION SCIENCES",
            "ANATCELL": "ANATOMY AND CELL BIOLOGY",
            "ANTHRO": "ANTHROPOLOGY",
            "APPLMATH": "APPLIED MATHEMATICS",
            "ARABIC": "ARABIC",
            "ARTHIST": "ART HISTORY",
            "ASTRON": "ASTRONOMY",
            "BME": "BME",
            "BIOCHEM": "BIOCHEMISTRY",
            "BIOLOGY": "BIOLOGY",
            "BIOSTAT": "BIOSTATISTICS",
            "BLACKST": "BLACK STUDIES",
            "BUS": "BUSINESS ADMINISTRATION",
            "BUSADMIN": "BUSINESS ADMINISTRATION",
            "CGS": "CENTRE FOR GLOBAL STUDIES",
            "CALC": "CALCULUS",
            "CALCULUS": "CALCULUS",
            "CHEMBENG": "CHEMICAL AND BIOCHEMICAL ENGINEERING",
            "CHEM": "CHEMISTRY",
            "CHILDYTH": "CHILDHOOD AND YOUTH STUDIES",
            "CHINESE": "CHINESE",
            "CLASSICS": "CLASSICAL STUDIES",
            "COMMSCI": "COMMUNICATION SCIENCES AND DISORDERS",
            "CSD": "COMMUNICATION SCIENCES AND DISORDERS",
            "COMPLITC": "COMPARATIVE LITERATURE AND CULTURE",
            "COMPSCI": "COMPUTER SCIENCE",
            "CS": "COMPUTER SCIENCE",
            "DATASCI": "DATA SCIENCE",
            "DIGCOMM": "DIGITAL COMMUNICATION",
            "DH": "DIGITAL HUMANITIES",
            "DISABST": "DISABILITY STUDIES",
            "EARTHSCI": "EARTH SCIENCES",
            "ECON": "ECONOMICS",
            "ENGSCI": "ENGINEERING SCIENCE",
            "ENGLISH": "ENGLISH",
            "ENVSCI": "ENVIRONMENTAL SCIENCE",
            "EPID": "EPIDEMIOLOGY",
            "EPIDBIO": "EPIDEMIOLOGY AND BIOSTATISTICS",
            "FAMSTUD": "FAMILY STUDIES AND HUMAN DEVELOPMENT",
            "FINMOD": "FINANCIAL MODELLING",
            "FRENCH": "FRENCH",
            "GLE": "GOVERNANCE, LEADERSHIP AND ETHICS",
            "GSWS": "GSWS",
            "GEOG": "GEOGRAPHY",
            "GERMAN": "GERMAN",
            "GREEK": "GREEK",
            "HLTHSCI": "HEALTH SCIENCES",
            "HEBREW": "HEBREW",
            "HISTORY": "HISTORY",
            "INDIGEN": "INDIGENOUS STUDIES",
            "INTGSCI": "INTEGRATED SCIENCE",
            "INTCOMM": "INTERCULTURAL COMMUNICATIONS",
            "ITALIAN": "ITALIAN",
            "JAPANESE": "JAPANESE",
            "KIN": "KINESIOLOGY",
            "LAW": "LAW",
            "LING": "LINGUISTICS",
            "MOS": "MANAGEMENT AND ORGANIZATIONAL STUDIES",
            "MATH": "MATHEMATICS",
            "MEDIACOM": "MEDIACOM",
            "MEDBIO": "MEDICAL BIOINFORMATICS",
            "MEDBPHYS": "MEDICAL BIOPHYSICS",
            "MEDSCI": "MEDICAL SCIENCES",
            "MICROIMM": "MICROBIOLOGY AND IMMUNOLOGY",
            "MUSEUMS": "MUSEUM AND CURATORIAL STUDIES",
            "NEURO": "NEUROSCIENCE",
            "NMM": "NUMERICAL AND MATHEMATICAL METHODS",
            "NURSING": "NURSING",
            "ONEHLTH": "ONE HEALTH",
            "PATH": "PATHOLOGY",
            "PERSIAN": "PERSIAN",
            "PHARM": "PHARMACOLOGY",
            "PHIL": "PHILOSOPHY",
            "PHYSIC": "PHYSICS",
            "PHYSICS": "PHYSICS",
            "PHYSIOL": "PHYSIOLOGY",
            "PHYSPHRM": "PHYSIOLOGY AND PHARMACOLOGY",
            "POLISCI": "POLITICAL SCIENCE",
            "PSYCH": "PSYCHOLOGY",
            "RELSTUD": "RELIGIOUS STUDIES",
            "SCIENCE": "SCIENCE",
            "SOC": "SOCIOLOGY",
            "SPANISH": "SPANISH",
            "STATSCI": "STATISTICAL SCIENCES",
            "WRITING": "WRITING",
        }
        
        abbrev_to_full = {}
        full_to_abbrev = {}

        # Load hardcoded abbreviations first
        for abbrev, full in KNOWN_ABBREVIATIONS.items():
            abbrev_to_full[abbrev] = full
            abbrev_to_full[full] = full
            full_to_abbrev[full] = abbrev
        
        # Method 1: Use subject_code field (when populated)
        for course in self.courses_data.get("courses", {}).values():
            subject_code = course.get("subject_code", "").strip().upper()
            course_title = course.get("course_title", "").strip()
            
            if not subject_code or not course_title:
                continue
                
            match = re.match(r'^(.+?)\s+\d{4}', course_title)
            if match:
                full_name = match.group(1).strip().upper()
                abbrev_to_full[subject_code] = full_name
                abbrev_to_full[full_name] = full_name
                full_to_abbrev[full_name] = subject_code
        
        # Method 2: Use course KEYS in western_courses.json (e.g. "COMPSCI_2208AB")
        for key, course in self.courses_data.get("courses", {}).items():
            course_title = course.get("course_title", "").strip()
            if not course_title:
                continue
            
            match = re.match(r'^(.+?)\s+\d{4}', course_title)
            if not match:
                continue
            full_name = match.group(1).strip().upper()
            
            key_match = re.match(r'^([A-Z]+)_\d{4}', key.upper())
            if key_match:
                abbrev = key_match.group(1)
                abbrev_to_full[abbrev] = full_name
                abbrev_to_full[full_name] = full_name
                full_to_abbrev[full_name] = abbrev
        
        # Method 3: Scan module course lists for full names
        for module in self.modules_data.get("modules", {}).values():
            for group in module.get("course_groups", []):
                for course in group.get("courses", []):
                    name = course.get("name", "")
                    match = re.match(r'^(.+?)\s+\d{4}', name)
                    if match:
                        full_name = match.group(1).strip().upper()
                        abbrev_to_full[full_name] = full_name
        
        print(f"Built abbreviation map with {len(abbrev_to_full)} entries.")
        return abbrev_to_full
            
    def normalize_course(self, course_str: str) -> str:
        """
        Normalize a course string to a canonical format.
        e.g. 'Calculus 1000A/B' -> 'CALCULUS 1000'
             'COMPSCI 2208A'    -> 'COMPUTER SCIENCE 2208'
        """
        if not course_str:
            return ""
        course_str = str(course_str).upper().strip()
        match = re.search(r'([A-Z\s\-]+?)\s*(\d{4})', course_str)
        if match:
            subject = match.group(1).strip()
            num = match.group(2)
            # Resolve abbreviation to canonical full name
            canonical = self.abbrev_map.get(subject, subject)
            return f"{canonical} {num}"
        return course_str

    def check_course_match(self, required_str: str, student_courses_normalized: List[str]) -> bool:
        """Check if required_str (e.g. 'Computer Science 1026A/B') is satisfied by student courses"""
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
                
                courses_len = len(group.get("courses", []))
                if courses_len > 0:
                    proportion = len(group_res["courses_met"]) / courses_len
                    group_res["credits_met"] = round(credits_required * proportion, 2)
                    group_res["is_met"] = len(group_res["courses_missing"]) == 0
                    
            elif group_type == "choose_from":
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
        norm_name = self.normalize_course(course_name)
        for c_data in self.courses_data.get("courses", {}).values():
            if self.normalize_course(c_data.get("course_title", "")) == norm_name:
                w = c_data.get("course_weight")
                try:
                    return float(w) if w else 0.5
                except:
                    return 0.5
        return 0.5
