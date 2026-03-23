# Data Fetching Architecture

This repository contains a web crawler (`crawler.py`) designed to scrape course information from the Western University Academic Calendar.

## Overview

The fetching process is implemented in the `WesternCrawler` class, which uses the `requests` library to fetch HTML pages and `BeautifulSoup` (`bs4`) to parse and extract the required data. The crawler follows a hierarchical, three-step approach:
1. Fetch all subjects.
2. Fetch all courses for each subject.
3. Fetch detailed information for each specific course.

The scraped data is saved progressively to `western_courses.json`.

## Fetching Steps

### 1. Subject Discovery (`get_subjects`)
- **Endpoint**: `https://www.westerncalendar.uwo.ca/Courses.cfm`
- **Methodology**: 
  - The crawler requests the main courses page and parses it.
  - It looks for `<a>` tags where the `href` attribute contains `Subject=`.
  - It extracts the subject code from the URL query parameters and builds a list of unique subject URLs.

### 2. Course Discovery (`get_courses`)
- **Endpoint**: The specific subject URL obtained in the previous step.
- **Methodology**: 
  - For each subject URL, the crawler requests the page and parses the HTML.
  - It searches for `<a>` tags with `href` attributes containing `CourseAcadCalendarID=`.
  - It prioritizes links that contain the text "More details", but falls back to any link with a `CourseAcadCalendarID` if no "More details" links are found.
  - It compiles a list of unique course detail URLs for that subject.

### 3. Course Details Extraction (`get_course_details`)
- **Endpoint**: The specific course detail URL.
- **Methodology**: 
  - The crawler requests the individual course page and meticulously extracts data fields based on HTML structure:
    - **Course ID**: Parsed directly from the URL query parameter `CourseAcadCalendarID`.
    - **Course Title**: Extracted from the first valid `<h2>` tag.
    - **Informal Name**: Extracted from an `<h3>` tag (avoiding known system headers).
    - **Properties (Weight, Breadth, Subject Code)**: Extracted from `<h5>` tags by matching text labels like "Course Weight:", "Breadth:", and "Subject Code:".
    - **Prerequisites & Antirequisites**: Located by finding `<label>` tags with the class `novecentoMedium` containing the specific text (e.g., "Prerequisite", "Antirequisite") and then extracting text and links from their next sibling `<div>`.
    - **Modules**: Extracted by finding `<a>` tags where the `href` contains `Modules.cfm?ModuleID=`. The link text is split by `|` to parse faculty, study type, and program name.

## Data Storage

The data is stored in the `western_courses.json` file. The structure is a dictionary with a `courses` key. 
Inside `courses`, each course is stored as a key-value pair:
- **Key**: A unique identifier combining the subject code and course number (e.g., `COMPSCI_1026A`), or the raw ID if parsing fails.
- **Value**: A dictionary containing all the extracted details (`id`, `url`, `course_title`, `informal_name`, `course_weight`, `breadth`, `subject_code`, `antirequisites`, `prerequisites`, `modules`).

The crawler saves the state to this JSON file after *every single* course is successfully fetched. This ensures that progress is not lost if the crawler is interrupted or crashes. It also includes logic in `load_data()` to resume from the existing `western_courses.json` file on startup.

## Rate Limiting and Anti-Scraping Measures

To prevent overwhelming the target server and to handle soft blocks gracefully, the crawler implements several strategies:
- **User-Agent Header**: Sets a standard modern browser user agent.
- **Request Retries (`fetch_with_retry`)**: Wraps HTTP requests allowing up to 3 retries (or more in specific functions) with random delays (2.0s to 5.0s) between failures.
- **Human-like Delays**: Employs substantial randomized sleep intervals between requests:
  - `0.5s` to `3.0s` delay after failed subject fetches.
  - `10.0s` to `20.0s` delay if 0 courses are found for a subject.
  - `10.0s` to `50.0s` artificial delay after processing each individual course to mimic manual browsing speed.
