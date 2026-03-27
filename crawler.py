import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import json
import time
import re

class WesternCrawler:
    BASE_URL = "https://www.westerncalendar.uwo.ca/"
    COURSES_URL = "https://www.westerncalendar.uwo.ca/Courses.cfm"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.output_file = "western_courses.json"
        self.modules_file = "western_modules.json"
        
        # Load manual session cookies to bypass CAPTCHA
        import os
        if os.path.exists("cookies.json"):
            with open("cookies.json", "r") as f:
                self.session.cookies.update(json.load(f))
                print("Loaded manual session cookies from cookies.json.")
                
        self.courses_data = self.load_data()
        self.modules_data = self.load_modules()

    def load_data(self):
        try:
            with open(self.output_file, "r") as f:
                data = json.load(f)
                print(f"Loaded {len(data.get('courses', {}))} existing courses.")
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"courses": {}}

    def save_data(self):
        with open(self.output_file, "w") as f:
            json.dump(self.courses_data, f, indent=2)

    def fetch_with_retry(self, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                # Random user agent rotation could happen here if we had a list
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
                if attempt < max_retries - 1:
                     import random
                     time.sleep(random.uniform(2.0, 5.0))
        return None

    def get_subjects(self):
        print(f"Fetching subjects from {self.COURSES_URL}...")
        
        max_retries = 10
        for attempt in range(max_retries):
            response = self.fetch_with_retry(self.COURSES_URL)
            if not response:
                if attempt < max_retries - 1:
                    continue
                return []

            try:
                soup = BeautifulSoup(response.text, "html.parser")
                
                subjects = []
                for a_tag in soup.find_all("a", href=True):
                    href = a_tag["href"]
                    if "Subject=" in href:
                        full_url = urljoin(self.BASE_URL, href)
                        parsed_url = urlparse(full_url)
                        query_params = parse_qs(parsed_url.query)
                        subject_code = query_params.get("Subject", [None])[0]
                        
                        if subject_code:
                            subjects.append({
                                "code": subject_code,
                                "url": full_url
                            })
                
                unique_subjects = {s["code"]: s for s in subjects}.values()
                
                if len(unique_subjects) > 0:
                    print(f"Found {len(unique_subjects)} subjects.")
                    return list(unique_subjects)
                
                print(f"WARNING: Found 0 subjects (Attempt {attempt + 1}/{max_retries}).")
                print(f"Status Code: {response.status_code}")
                title = soup.find("title")
                print(f"Page Title: {title.get_text(strip=True) if title else 'No Title'}")
                h3 = soup.find("h3")
                print(f"First H3: {h3.get_text(strip=True) if h3 else 'No H3'}")
                print("Retrying...")
                
                import random
                time.sleep(random.uniform(0.5, 3.0)) # Long wait for soft block

            except Exception as e:
                print(f"Error fetching subjects: {e}")
        
        return []

    def get_courses(self, subject_url):
        print(f"Fetching courses from {subject_url}...")
        
        max_retries = 4
        for attempt in range(max_retries):
            response = self.fetch_with_retry(subject_url)
            if not response:
                if attempt < max_retries - 1:
                    continue
                return []

            try:
                soup = BeautifulSoup(response.text, "html.parser")
                
                course_links = []
                for a_tag in soup.find_all("a", href=True):
                    href = a_tag["href"]
                    if "CourseAcadCalendarID=" in href and "More details" in a_tag.get_text(strip=True):
                        full_url = urljoin(self.BASE_URL, href)
                        course_links.append(full_url)
                
                if not course_links:
                     for a_tag in soup.find_all("a", href=True):
                        href = a_tag["href"]
                        if "CourseAcadCalendarID=" in href:
                             full_url = urljoin(self.BASE_URL, href)
                             course_links.append(full_url)

                unique_links = list(set(course_links))
                
                if len(unique_links) > 0:
                    print(f"Found {len(unique_links)} courses.")
                    return unique_links
                
                print(f"WARNING: Found 0 courses (Attempt {attempt + 1}/{max_retries}). Retrying...")
                import random
                time.sleep(random.uniform(10.0, 20.0)) # Long wait for soft block

            except Exception as e:
                print(f"Error fetching courses for {subject_url}: {e}")
        
        return []

    def get_course_details(self, course_url):
        print(f"Fetching details from {course_url}...")
        response = self.fetch_with_retry(course_url)
        if not response:
            return None

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract ID from URL for key
            parsed_url = urlparse(course_url)
            query_params = parse_qs(parsed_url.query)
            course_id = query_params.get("CourseAcadCalendarID", ["UNKNOWN"])[0]

            # Parse details
            # Course Weight, Breadth, Subject Code first to help with title matching
            course_weight = ""
            breadth = ""
            subject_code = ""

            for h5 in soup.find_all("h5"):
                text = h5.get_text(strip=True)
                if "Course Weight:" in text:
                    course_weight = text.split("Course Weight:")[-1].strip()
                    try:
                        course_weight = float(course_weight)
                    except ValueError:
                        pass
                elif "Breadth:" in text:
                    breadth = text.split("Breadth:")[-1].strip().rstrip(" i") # remove ' i' info icon text
                elif "Subject Code:" in text:
                    subject_code = text.split("Subject Code:")[-1].strip()

            # Course Title (often in h2)
            course_title = ""
            for h2 in soup.find_all("h2"):
                text = h2.get_text(strip=True)
                if any(x in text for x in ["Academic Calendar", "Courses by Subject", "Filter By"]):
                    continue
                if len(text) > 5:
                    course_title = text
                    break
            
            # Informal Name (h3)
            # The page structure puts the informal name in an h3, often following the h2.
            # We want the first h3 that is not a page header or hidden/system element.
            informal_name = ""
            for h3 in soup.find_all("h3"):
                # Avoid known system headers if any (like "Academic Calendar" if it uses h3)
                if "pageTitleHeader" in h3.get("class", []):
                     continue
                text = h3.get_text(strip=True)
                if text and text != "MATHEMATICS FOR FINANCIAL ANALYSIS":
                    informal_name = text
                    break

            # Prerequisites and Antirequisites
            antirequisites = {"text": "", "courses": []}
            prerequisites = {"text": "", "courses": []}

            # Helper to extract info from the labeled divs
            def extract_labeled_section(label_text):
                section_data = {"text": "", "courses": []}
                # Find label with specific text
                # The label has class "novecentoMedium borderBottom"
                labels = soup.find_all("label", class_="novecentoMedium")
                for label in labels:
                    if label_text in label.get_text(strip=True):
                        # The content is in the div sibling or parent's sibling?
                        # From debug: label is inside a div class="col-xs-12". The content is in a div following the label.
                        # <div class="col-xs-12"> <label>...</label> <div> CONTENT </div> </div>
                        content_div = label.find_next_sibling("div")
                        if content_div:
                            section_data["text"] = content_div.get_text(strip=True)
                            # Find links
                            for a in content_div.find_all("a", href=True):
                                link_text = a.get_text(strip=True)
                                link_url = urljoin(self.BASE_URL, a["href"])
                                if "Courses.cfm" in link_url:
                                    section_data["courses"].append({
                                        "name": link_text,
                                        "url": link_url
                                    })
                        break
                return section_data

            antirequisites = extract_labeled_section("Antirequisite")
            prerequisites = extract_labeled_section("Pre or Corequisites")
            
            if not prerequisites["text"]:
                 prerequisites = extract_labeled_section("Prerequisite")

            # Modules
            modules = []
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                if "Modules.cfm?ModuleID=" in href:
                    module_text = a_tag.get_text(strip=True)
                    if "|" in module_text:
                        parts = [p.strip() for p in module_text.split("|")]
                        if len(parts) >= 3:
                            modules.append({
                                "faculty": parts[0],
                                "study": parts[1],
                                "program": parts[-1], # The last part is the program name
                                "program_type": parts[-1].split(" IN ")[0].title() if " IN " in parts[-1] else "Unknown",
                                "url": urljoin(self.BASE_URL, href)
                            })

            return {
                "id": course_id,
                "url": course_url,
                "course_title": course_title,
                "informal_name": informal_name,
                "course_weight": course_weight,
                "breadth": breadth,
                "subject_code": subject_code,
                "antirequisites": antirequisites,
                "prerequisites": prerequisites,
                "modules": modules
            }

        except Exception as e:
            print(f"Error fetching details for {course_url}: {e}")
            return None

    def load_modules(self):
        try:
            with open(self.modules_file, "r") as f:
                data = json.load(f)
                print(f"Loaded {len(data.get('modules', {}))} existing modules.")
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"modules": {}}

    def save_modules(self):
        with open(self.modules_file, "w") as f:
            json.dump(self.modules_data, f, indent=2)

    def get_module_details(self, module_url):
        """Scrape a module page and extract structured requirement data."""
        print(f"Fetching module from {module_url}...")
        response = self.fetch_with_retry(module_url)
        if not response:
            return None

        try:
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract module ID from URL
            parsed_url = urlparse(module_url)
            query_params = parse_qs(parsed_url.query)
            module_id = query_params.get("ModuleID", ["UNKNOWN"])[0]

            # Module name and type from <h2>
            module_name = ""
            module_type = ""
            faculty = ""
            department = ""

            if "One more thing... Please confirm you are indeed a person" in soup.get_text():
                return {"error": "captcha"}


            h2 = soup.find("h2")
            if h2:
                # Type from the icon <img> inside h2
                icon_img = h2.find("img")
                if icon_img:
                    module_type = icon_img.get("title", "").strip()

                # Name is the text of h2 excluding the <small> tag
                small_tag = h2.find("small")
                if small_tag:
                    faculty_dept = small_tag.get_text(strip=True)
                    # Format: "Faculty of Science - Statistical and Actuarial Sciences"
                    if " - " in faculty_dept:
                        parts = faculty_dept.split(" - ", 1)
                        faculty = parts[0].strip()
                        department = parts[1].strip()
                    else:
                        faculty = faculty_dept

                # Module name = h2 text minus small text minus img alt
                h2_text = h2.get_text(strip=True)
                if small_tag:
                    h2_text = h2_text.replace(small_tag.get_text(strip=True), "").strip()
                if icon_img and icon_img.get("alt"):
                    h2_text = h2_text.replace(icon_img.get("alt", ""), "").strip()
                module_name = h2_text

            # Admission Requirements
            admission_text = ""
            admission_courses = []
            adm_div = soup.find("div", id="AdmissionRequirements")
            if adm_div:
                admission_text = adm_div.get_text(strip=True)
                for a_tag in adm_div.find_all("a", href=True):
                    href = a_tag["href"]
                    if "Courses.cfm" in href:
                        admission_courses.append({
                            "name": a_tag.get_text(strip=True).rstrip(","),
                            "url": urljoin(self.BASE_URL, href)
                        })

            # Module/Program Information (course groups)
            course_groups = []
            total_courses = 0.0
            notes = ""

            module_div = soup.find("div", class_="moduleInfo")
            if module_div:
                module_text = module_div.get_text()

                # Extract total courses from "Module X.X courses:"
                total_match = re.search(r'Module\s*(\d+\.?\d*)\s*courses?:', module_text)
                if total_match:
                    total_courses = float(total_match.group(1))

                # Use raw HTML and split on <br> variants for reliable parsing
                # BS4's html.parser nests content inside <br> tags incorrectly
                raw_html = str(module_div)
                
                # Split on <br>, <br/>, <br />
                segments = re.split(r'<br\s*/?>', raw_html)

                for segment in segments:
                    seg_soup = BeautifulSoup(segment, "html.parser")
                    seg_text = seg_soup.get_text(strip=True)

                    if not seg_text:
                        continue

                    # Skip "Module" header and div wrappers
                    if seg_text in ("Module", "") or seg_text.startswith("<div"):
                        continue

                    # Strip leading "X.X courses:" header if concatenated (e.g., "6.0 courses:2.0 courses:...")
                    header_strip = re.match(r'(\d+\.?\d*)\s*courses?:\s*(.*)', seg_text, re.DOTALL)
                    if header_strip and header_strip.group(2) and re.match(r'\d+\.?\d*\s+', header_strip.group(2)):
                        # This is "6.0 courses:2.0 courses:..." - strip the header
                        seg_text = header_strip.group(2)
                        # Re-parse segment HTML to also strip the header part
                        # Find where the actual group starts in the HTML
                    
                    # Match "X.X courses:" or "X.X course:" or "X.X course from:" 
                    credit_match = re.match(
                        r'(\d+\.?\d*)\s+courses?\s*(from\s*)?:\s*(.*)',
                        seg_text, re.IGNORECASE | re.DOTALL
                    )

                    if credit_match:
                        credits = float(credit_match.group(1))
                        is_from = credit_match.group(2) is not None
                        
                        # Extract linked courses
                        linked_courses = []
                        for a_tag in seg_soup.find_all("a", href=True):
                            href = a_tag["href"]
                            if "Courses.cfm" in href:
                                linked_courses.append({
                                    "name": a_tag.get_text(strip=True).rstrip(","),
                                    "url": urljoin(self.BASE_URL, href)
                                })

                        if is_from:
                            group = {
                                "credits": credits,
                                "type": "choose_from",
                                "courses": linked_courses,
                                "description": seg_text
                            }
                        else:
                            group = {
                                "credits": credits,
                                "type": "required",
                                "courses": linked_courses
                            }
                        course_groups.append(group)
                        continue

                    # Match "X.X additional ..." patterns 
                    additional_match = re.match(
                        r'(\d+\.?\d*)\s*\xa0?additional\s+(.*)',
                        seg_text, re.IGNORECASE
                    )
                    if additional_match:
                        credits = float(additional_match.group(1))
                        linked_courses = []
                        for a_tag in seg_soup.find_all("a", href=True):
                            if "Courses.cfm" in a_tag["href"]:
                                linked_courses.append({
                                    "name": a_tag.get_text(strip=True).rstrip(","),
                                    "url": urljoin(self.BASE_URL, a_tag["href"])
                                })
                        course_groups.append({
                            "credits": credits,
                            "type": "additional",
                            "description": seg_text,
                            "courses": linked_courses
                        })
                        continue

                    # Notes: substitution rules, general notes
                    if ("Note:" in seg_text or "may be replaced" in seg_text 
                            or "may be substituted" in seg_text or "can only be" in seg_text):
                        if notes:
                            notes += " "
                        notes += seg_text

            return {
                "module_id": module_id,
                "name": module_name,
                "type": module_type,
                "faculty": faculty,
                "department": department,
                "admission_requirements": {
                    "text": admission_text,
                    "courses": admission_courses
                },
                "total_courses": total_courses,
                "course_groups": course_groups,
                "notes": notes,
                "url": module_url
            }

        except Exception as e:
            print(f"Error fetching module {module_url}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_all_module_urls(self):
        """Extract all unique module URLs from the crawled course data."""
        module_urls = {}
        for course in self.courses_data.get("courses", {}).values():
            for module in course.get("modules", []):
                url = module.get("url", "")
                if url:
                    parsed = urlparse(url)
                    mid = parse_qs(parsed.query).get("ModuleID", [""])[0]
                    if mid:
                        module_urls[mid] = url
        print(f"Found {len(module_urls)} unique modules in course data.")
        return module_urls

    def crawl_modules(self):
        """Crawl all module pages and save to western_modules.json."""
        module_urls = self.get_all_module_urls()

        for i, (mid, url) in enumerate(module_urls.items()):
            # Skip if already crawled
            if mid in self.modules_data.get("modules", {}):
                print(f"[{i+1}/{len(module_urls)}] Skipping module {mid} (already crawled)")
                continue

            print(f"[{i+1}/{len(module_urls)}] Crawling module {mid}...")
            details = self.get_module_details(url)

            if details:
                if details.get("error") == "captcha":
                    print("CAPTCHA detected! Stopping crawl immediately.")
                    break
                self.modules_data["modules"][mid] = details
                self.save_modules()
                print(f"  -> Saved: {details['name']}")
            else:
                print(f"  -> FAILED to fetch module {mid}")

            # Rate limit - significantly increased to bypass bot protection
            import random
            time.sleep(random.uniform(15.0, 25.0))

        print(f"Module crawling complete. {len(self.modules_data['modules'])} modules saved to {self.modules_file}")

    def run(self):
        subjects = self.get_subjects()
        
        for i, subject in enumerate(subjects):
            print(f"[{i+1}/{len(subjects)}] Processing subject: {subject['code']}")
            base_course_url = subject["url"]
            course_links = self.get_courses(base_course_url)
            
            for link in course_links:
                # Check if we already have this course to skip redundant work
                # Note: We can't easily check by key before fetching details because key depends on details
                # But we can check by ID if we parse it from link.
                parsed_link = urlparse(link)
                link_id = parse_qs(parsed_link.query).get("CourseAcadCalendarID", [""])[0]
                
                # Check if this ID is already in our data (values)
                # This is inefficient O(N) but safer. Or we can just re-crawl.
                # Given user wants to append/fix, let's just crawl.
                
                details = self.get_course_details(link)
                if details:
                     # Create a unique key combining subject + course number (or just use parsed ID)
                    key = f"{details['subject_code']}_{details['course_title'].split()[-1].replace('/', '')}" if details['subject_code'] and details['course_title'] else details['id']
                    
                    if details['course_title']:
                         parts = details['course_title'].split()
                         if len(parts) > 0:
                             course_num = parts[-1].replace("/", "")
                             key = f"{details['subject_code']}_{course_num}"

                    self.courses_data["courses"][key] = details
                    self.save_data() # Save after every course

                # Random delay to be more human-like
                import random
                time.sleep(random.uniform(10.0, 50.0)) 

        print("Crawling complete. Data saved to western_courses.json")

if __name__ == "__main__":
    crawler = WesternCrawler()
    crawler.run()
