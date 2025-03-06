import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URL for the AP Calculus AB past exam questions page.
#Change this for the AP Class we want to scrape
base_url = "https://apcentral.collegeboard.org/courses/ap-calculus-ab/exam/past-exam-questions"

# Retrieve the page content.
response = requests.get(base_url)
response.raise_for_status()  # Make sure the request was successful.
soup = BeautifulSoup(response.text, 'html.parser')

# Find all PDF links by looking for <a> tags with an href that contains '/media/pdf/'
pdf_links = soup.find_all("a", href=lambda href: href and "/media/pdf/" in href)

# Process each link.
for link in pdf_links:
    href = link.get("href")
    full_url = urljoin(base_url, href)
    
    # Attempt to extract the year from the file name.
    # Example file name: "ap24-frq-calculus-ab.pdf"
    match = re.search(r"ap(\d+)-", href, re.IGNORECASE)
    if not match:
        print(f"Could not find a year in the link: {href}")
        continue

    year_str = match.group(1)
    # If the year is two digits, decide whether it belongs to 1900s or 2000s.
    if len(year_str) == 2:
        year_int = int(year_str)
        # This threshold may be adjusted if older materials exist.
        if year_int < 50:
            year_full = "20" + year_str
        else:
            year_full = "19" + year_str
    else:
        year_full = year_str

    # Create a folder for this year.
    os.makedirs(year_full, exist_ok=True)
    
    # Use the anchor text as the file name, cleaning it up and appending '.pdf'.
    # For example: "Free-Response Questions" becomes "Free-Response-Questions.pdf"
    file_name = link.get_text(strip=True).replace(" ", "_") + ".pdf"
    file_path = os.path.join(year_full, file_name)
    
    print(f"Downloading '{file_name}' for year {year_full} from {full_url}...")
    
    # Download the PDF file.
    file_response = requests.get(full_url)
    file_response.raise_for_status()
    
    with open(file_path, "wb") as f:
        f.write(file_response.content)
    
    print(f"Saved to: {file_path}")
