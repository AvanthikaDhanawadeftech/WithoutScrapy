import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

frontier = ["https://www.livemint.com/"]
visited = {}
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
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.text.strip()
    return "No Title"


def get_h2_tags(soup):
    h2_tags = soup.find_all("h2")
    return [tag.text.strip() for tag in h2_tags]


def get_images(soup, base_url):
    images = []
    for img in soup.find_all("img", src=True):
        img_url = urljoin(base_url, img["src"])
        alt_text = img.get("alt", "").strip()
        images.append((img_url, alt_text))
    return images


def save_image(img_url, folder="images"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    img_data = requests.get(img_url).content
    img_name = os.path.join(folder, os.path.basename(img_url))
    with open(img_name, "wb") as img_file:
        img_file.write(img_data)
    return img_name


while len(frontier) > 0 and len(visited) < max_urls:
    url_to_visit = frontier.pop()

    try:
        response = requests.get(url_to_visit)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url_to_visit}: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    page_title = get_page_title(soup)
    print(f"Title: {page_title}")
    candidate_links = parse_links(soup, url_to_visit)
    for current in candidate_links:
        if current not in visited:
            frontier.append(current)

    h2_tags = get_h2_tags(soup)
    print(f"H2 Tags: {h2_tags}")

    images = get_images(soup, url_to_visit)
    for img_url, alt_text in images:
        img_path = save_image(img_url)
        print(f"Saved Image: {img_path} (Alt: {alt_text})")

    unix_ts = int(datetime.now().timestamp())
    file_to_save = f"liveMint_{unix_ts}.html"
    with open(file_to_save, "w") as html_file:
        html_file.write(response.text)

    visited[url_to_visit] = {
        "timestamp": datetime.now().isoformat(),
        "title": page_title,
        "h2_tags": h2_tags,
        "images": images,
    }
print(f"Visited: {url_to_visit}")

print("Crawling finished.")
