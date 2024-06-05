import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import time

frontier = ["https://zeenews.india.com/"]
visited = set()  
max_urls = 1

def parse_links(soup, base_url):
    links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        full_url = urljoin(base_url, href)
        if full_url.startswith("http"):
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

def extract_data(soup):
    data = []
    news_articles = soup.find_all("div", class_="sec_box")
    for article in news_articles:
        image = article.find("img")["src"]
        title = article.find("h3").text.strip()
        data.append({"image": image, "title": title})
    return data

while len(frontier) > 0 and len(visited) < max_urls:
    url_to_visit = frontier.pop(0)  
    if url_to_visit in visited:
        continue

    try:
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url_to_visit, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url_to_visit}: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    page_title = get_page_title(soup)
    paragraphs = get_paragraphs(soup)
    images = get_images(soup, url_to_visit)

    print(f"Title: {page_title}")
    print(f"Paragraphs: {paragraphs}")
    print(f"Images: {images}")
    candidate_links = parse_links(soup, url_to_visit)
    for current in candidate_links:
        if current not in visited:
            frontier.append(current)


    data = extract_data(soup)

    
    for item in data:
        print("Title:", item["title"])

    
    for item in data:
        print("Image:", item["image"])
        print("Title:", item["title"])
        print()


    unix_ts = int(datetime.now().timestamp())
    file_to_save = f"zeenews_{unix_ts}.html"
    with open(file_to_save, "w", encoding="utf-8") as html_file:
        html_file.write(response.text)

    visited.add(url_to_visit)
    print(f"LINK: {url_to_visit}")


print("Scraping completed.")



