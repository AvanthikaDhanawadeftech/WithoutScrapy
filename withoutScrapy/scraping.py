
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

frontier = ["https://www.hindustantimes.com/"]
visited = {}
max_urls = 1
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def parse_links(soup, base_url):
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        if full_url.startswith('http'):
            links.append(full_url)
    return links

def get_page_title(soup):
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.text.strip()
    return "No Title"

def get_paragraphs(soup):
    paragraphs = []
    for p in soup.find_all('p'):
        paragraphs.append(p.text.strip())
    return paragraphs

def get_images(soup, base_url):
    images = []
    for img in soup.find_all('img', src=True):
        src = img['src']
        full_url = urljoin(base_url, src)
        images.append(full_url)
    return images

session = requests.Session()
session.headers.update(headers)

while len(frontier) > 0 and len(visited) < max_urls:
    url_to_visit = frontier.pop()
    try:
        response = session.get(url_to_visit)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url_to_visit}: {e}")
        continue

    soup = BeautifulSoup(response.text, 'html.parser')
    page_title = get_page_title(soup)
    paragraphs = get_paragraphs(soup)
    images = get_images(soup, url_to_visit)

    print(f"Title: {page_title}")
    print(f"Paragraphs: {paragraphs}")
    print(f"Images: {images}")
    candidate_links = parse_links(soup, url_to_visit)
    for current in candidate_links:
        if current not in visited and current not in frontier:
            frontier.append(current)

    unix_ts = int(datetime.now().timestamp())
    file_to_save = f'hindustantimes_{unix_ts}.html'
    with open(file_to_save, "w") as html_file:
        html_file.write(response.text)

    visited[url_to_visit] = datetime.now().isoformat()

    print(f"Visited: {url_to_visit}")


print("Crawling finished.")

