
import requests
from bs4 import BeautifulSoup

url = "https://www.westerncalendar.uwo.ca/Courses.cfm"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    print(r.text)
except Exception as e:
    print(f"Error: {e}")
