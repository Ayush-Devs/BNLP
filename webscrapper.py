import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from your_django_app.models import IEA  

class WebScraper:
    def __init__(self, url):
        self.url = url

    def scrape(self):
        """Scrapes the given URL and returns section details."""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless') 
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            driver.get(self.url)
            page_source = driver.page_source
            
            soup = BeautifulSoup(page_source, 'html.parser')
            driver.quit()

            
            section_data = {}
            sections = soup.find_all("div", class_="section-class")  
            for section in sections:
                section_title = section.find("h2").get_text(strip=True) 
                description = section.find("p").get_text(strip=True)  
                section_data[section_title] = description

            return section_data
        except Exception as e:
            print(f"Error during scraping: {e}")
            return {}

if __name__ == "__main__":
    url = os.getenv("LINK")
    if not url:
        raise ValueError("The 'LINK' environment variable is not set.")

    scraper = WebScraper(url)
    section_details = scraper.scrape()

    for section_title, description in section_details.items():
        match = re.match(r"Section (\d+[A-Za-z]*)\s[\u2013\u2014-]\s*(.+)", section_title)
        if match:
            section_no = match.group(1)
            section_name = match.group(2).strip()
            print(f"Processing Section: {section_no} - {section_name}")

            # Save to the database if it doesn't already exist
            if not IEA.objects.filter(section_id=section_no).exists():
                IEA(section_id=section_no, section_title=section_name, description=description).save()
                print(f"Saved: {section_no} - {section_name}")
            else:
                print(f"Section {section_no} already exists.")
        else:
            print(f"Skipping unmatched section title: {section_title}")
