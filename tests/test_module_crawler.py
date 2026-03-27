from crawler import WesternCrawler
import json

c = WesternCrawler()

# Test with 3 known modules
test_modules = [
    ("21050", "https://www.westerncalendar.uwo.ca/Modules.cfm?ModuleID=21050&SelectedCalendar=Live&ArchiveID="),  # Major in Actuarial Science
    ("21053", "https://www.westerncalendar.uwo.ca/Modules.cfm?ModuleID=21053&SelectedCalendar=Live&ArchiveID="),  # Honours Spec Actuarial Science
    ("20805", "https://www.westerncalendar.uwo.ca/Modules.cfm?ModuleID=20805&SelectedCalendar=Live&ArchiveID="),  # Honours Spec Psychology
]

for mid, url in test_modules:
    print(f"\n{'='*60}")
    print(f"Testing Module {mid}")
    print(f"{'='*60}")
    
    details = c.get_module_details(url)
    
    if details:
        print(f"  Name:       {details['name']}")
        print(f"  Type:       {details['type']}")
        print(f"  Faculty:    {details['faculty']}")
        print(f"  Department: {details['department']}")
        print(f"  Total:      {details['total_courses']} courses")
        print(f"  Admission:  {details['admission_requirements']['text'][:100]}...")
        print(f"  Adm Courses:{len(details['admission_requirements']['courses'])}")
        print(f"  Notes:      {details['notes'][:100] if details['notes'] else 'None'}...")
        print(f"\n  Course Groups ({len(details['course_groups'])}):")
        for i, group in enumerate(details['course_groups']):
            courses_str = ", ".join([c['name'] for c in group.get('courses', [])])
            print(f"    [{i+1}] {group['credits']} credits | {group['type']}")
            if group['type'] == 'additional':
                print(f"        Desc: {group.get('description', '')[:80]}")
            if courses_str:
                print(f"        Courses: {courses_str[:80]}")
    else:
        print("  FAILED to fetch module details!")
    
    print()

print("All module tests complete!")
