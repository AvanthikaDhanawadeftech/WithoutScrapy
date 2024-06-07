import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import time
import json
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


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
    return "," . join(paragraphs)

def get_images(soup, base_url):
    images = set()  
    for img in soup.find_all('img', src=True):
        src = img['src']
        full_url = urljoin(base_url, src)
        images.add(full_url)
    return list(images) 

def extract_data(soup):
    data = []
    news_articles = soup.find_all("div", class_="sec_box")
    for article in news_articles:
        image = article.find("img")["src"]
        title = article.find("h3").text.strip()
        data.append({"image": image, "title": title})
    return data

def main():
    frontier = ["https://zeenews.india.com/"]
    visited = {}
    file_counter = 0
    data_to_save = []

    while len(frontier) > 0:
        url_to_visit = frontier.pop()
        try:
            response = requests.get(url_to_visit, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {url_to_visit}: {e}")
            continue

        if response.status_code == 200:
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

            
            data_to_save.append({
                'url': url_to_visit,
                'title': page_title,
                'paragraphs': paragraphs,
                'images': images,
                'timestamp': visited[url_to_visit]
            })

            file_counter += 1
    
            if file_counter >= 100:
                json_file_to_save = f'hindustantimes_data_{unix_ts}.json'
                with open(json_file_to_save, "w") as json_file:
                    json.dump(data_to_save, json_file, indent=4)
            
                file_counter = 0
                data_to_save = []

            print(f"Visited: {url_to_visit}")


    if data_to_save:
        unix_ts = int(datetime.now().timestamp())
        json_file_to_save = f'zeenews{unix_ts}.json'
        with open(json_file_to_save, "w") as json_file:
            json.dump(data_to_save, json_file, indent=4)

print("Crawling finished.")


if __name__ == "__main__":
    main()


