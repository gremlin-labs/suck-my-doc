import os
import json
import sys
import time
import argparse
from urllib.parse import urlparse, urljoin, quote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
CHROME_BINARY_PATH = os.getenv("CHROME_BINARY_PATH")

# Verify that the paths are set
if not CHROMEDRIVER_PATH or not CHROME_BINARY_PATH:
    print("Error: CHROMEDRIVER_PATH and CHROME_BINARY_PATH must be set in the .env file.")
    sys.exit(1)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Suck down documentation from a base URL.')
parser.add_argument('base_url', help='The base URL of the documentation site to scrape.')
parser.add_argument('-all', action='store_true', help='Scrape all pages, not just those under /docs.')
parser.add_argument('-csection', action='store_true', help='Save each documentation section into its own file.')
parser.add_argument('-solo', action='store_true', help='Scrape only the provided documentation URL and then stop.')
args = parser.parse_args()

base_url = args.base_url.rstrip('/')
scrape_all = args.all
split_sections = args.csection
solo_mode = args.solo

def setup_webdriver():
    chrome_service = Service(CHROMEDRIVER_PATH)
    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY_PATH
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=chrome_service, options=chrome_options)

def get_navigation_links(url, driver):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(2)  # Allow time for dynamic content to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    links = []

    nav_elements = soup.find_all(['nav', 'ul', 'ol', 'div'], class_=['navigation', 'menu', 'sidebar'])

    if not nav_elements:
        nav_elements = [soup]

    for nav in nav_elements:
        for a in nav.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if text and is_valid_url(href, base_url):
                links.append({"title": text, "url": urljoin(base_url, href)})

    return list({v['url']: v for v in links}.values())  # Remove duplicates

def is_valid_url(url, base_url):
    parsed_url = urlparse(urljoin(base_url, url))
    parsed_base = urlparse(base_url)
    return (parsed_url.netloc == parsed_base.netloc and
            (scrape_all or '/docs' in parsed_url.path or parsed_url.path == parsed_base.path))

def scrape_page(url, driver):
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        content = {'url': url}

        content['title'] = soup.find('h1').get_text(strip=True) if soup.find('h1') else soup.title.string

        main_content = extract_main_content(soup)
        content['content'] = main_content

        content['code_examples'] = [code.get_text(strip=True) for code in soup.find_all('pre')]

        faqs = extract_faqs(soup)
        if faqs:
            content['faq'] = faqs

        return content
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def extract_main_content(soup):
    main_selectors = ['[role="main"]', '.main-content', '#main-content', '.content', '#content', 'article', '.docSearch-content']
    for selector in main_selectors:
        main = soup.select_one(selector)
        if main:
            return ' '.join(p.get_text(strip=True) for p in main.find_all('p'))

    return ' '.join(p.get_text(strip=True) for p in soup.find_all('p'))

def extract_faqs(soup):
    faq_selectors = ['.faq', '.faqs', '#faq', '#faqs']
    for selector in faq_selectors:
        faq_section = soup.select_one(selector)
        if faq_section:
            return [
                {
                    "question": q.get_text(strip=True),
                    "answer": a.get_text(strip=True)
                }
                for q, a in zip(faq_section.find_all('h3'), faq_section.find_all('p'))
            ]
    return []

def crawl_links(url, visited_urls, sections, driver):
    if url in visited_urls:
        return
    visited_urls.add(url)
    print(f"Scraping section: ({url})")
    section_data = scrape_page(url, driver)
    if section_data:
        sections.append((url, section_data))

        new_links = get_navigation_links(url, driver)
        for link in new_links:
            if link['url'] not in visited_urls:
                crawl_links(link['url'], visited_urls, sections, driver)

def save_json(data, filename):
    with open(filename, "w", encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

def main():
    print(f"Starting to scrape documentation from {base_url}")

    output_dir = 'documentation'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    parsed_url = urlparse(base_url)
    domain = parsed_url.netloc.replace('.', '_')

    driver = setup_webdriver()

    try:
        if solo_mode:
            print(f"Scraping single page in solo mode: {base_url}")
            section_data = scrape_page(base_url, driver)
            if section_data:
                section_name = section_data['title'].lower().replace(' ', '_')
                section_name = quote(section_name, safe='')
                output_filename = f"{domain}_docs_section_{section_name}-solo.json"
                output_path = os.path.join(output_dir, output_filename)
                save_json(section_data, output_path)
                print(f"Scraping completed. Data saved to '{output_path}'.")
        else:
            sections = []
            visited_urls = set()
            crawl_links(base_url, visited_urls, sections, driver)

            if split_sections:
                for url, section_data in sections:
                    section_name = section_data['title'].lower().replace(' ', '_')
                    section_name = quote(section_name, safe='')
                    output_filename = f"{domain}_docs_section_{section_name}.json"
                    output_path = os.path.join(output_dir, output_filename)
                    save_json(section_data, output_path)
                print(f"Scraping completed. Individual section files saved in '{output_dir}'.")
            else:
                doc_data = {"title": f"Documentation for {base_url}", "sections": [data for _, data in sections]}
                output_filename = f"{domain}_docs.json"
                output_path = os.path.join(output_dir, output_filename)
                save_json(doc_data, output_path)
                print(f"Scraping completed. Data saved to '{output_path}'.")

    except Exception as e:
        print(f"An error occurred during scraping: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
