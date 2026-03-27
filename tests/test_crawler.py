from crawler import WesternCrawler

c = WesternCrawler()

# Step 1: Test subject discovery
subjects = c.get_subjects()
print(f"Total subjects found: {len(subjects)}")
print(f"First 5: {[s['code'] for s in subjects[:5]]}")
print()

# Step 2: Test course discovery for first subject
first = subjects[0]
courses = c.get_courses(first['url'])
print(f"Courses in {first['code']}: {len(courses)}")
if courses:
    print(f"Sample URL: {courses[0]}")
print()

# Step 3: Test fetching details for one course
if courses:
    details = c.get_course_details(courses[0])
    if details:
        print("Course details fetched successfully:")
        print(f"  Title: {details['course_title']}")
        print(f"  Weight: {details['course_weight']}")
        print(f"  Breadth: {details['breadth']}")
        print(f"  Subject: {details['subject_code']}")
        print(f"  Modules: {len(details['modules'])}")
        print(f"  Prerequisites: {details['prerequisites']['text'][:80] if details['prerequisites']['text'] else 'None'}")
    else:
        print("Failed to fetch course details.")

print("\nAll tests passed!")
