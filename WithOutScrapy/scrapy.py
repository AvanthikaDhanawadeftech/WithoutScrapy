import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import json


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
    return "None"


def get_p_tags(soup):
    p_tags = soup.find_all("p")
    return [tag.text.strip() for tag in p_tags]


def main():
    frontier = [
        "https://www.livemint.com/market/stock-market-news/stock-market-today-sensex-nifty-50-extend-gains-into-2nd-consecutive-session-investors-earn-nearly-8-lakh-crore-11717667205581.html"
    ]
    visited = {}
    file_count = 0
    batch_size = 100
    all_data = []

    while len(frontier) > 0:
        url_to_visit = frontier.pop()

        try:
            response = requests.get(url_to_visit)
        except requests.RequestException as e:
            print(f"Failed to fetch {url_to_visit}: {e}")
            continue

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_title = get_page_title(soup)
            print(f"Title: {page_title}")
            candidate_links = parse_links(soup, url_to_visit)
            for current in candidate_links:
                if current not in visited:
                    frontier.append(current)

            p_tags = get_p_tags(soup)
            concatenated_p_tags = ",".join(p_tags)
            print(f"Paragraph Tags: {concatenated_p_tags}")

            unix_ts = int(datetime.now().timestamp())
            file_to_save = f"liveMint_{unix_ts}.html"
            with open(file_to_save, "w") as html_file:
                html_file.write(response.text)

            visited[url_to_visit] = {
                "timestamp": datetime.now().isoformat(),
                "title": page_title,
                "p_tags": p_tags,
            }

            all_data.append(
                {
                    "url": url_to_visit,
                    "timestamp": datetime.now().isoformat(),
                    "title": page_title,
                    "p_tags": concatenated_p_tags,
                }
            )

            file_count += 1

            if file_count % batch_size == 0:
                json_file_to_save = f"liveMint_data_{file_count // batch_size}.json"
                with open(json_file_to_save, "w") as json_file:
                    json.dump(all_data, json_file, indent=4)
                all_data.clear()

    if all_data:
        json_file_to_save = f"liveMint_data_batch_{(file_count // batch_size) + 1}.json"
        with open(json_file_to_save, "w") as json_file:
            json.dump(all_data, json_file, indent=4)

    print("Crawling finished.")


if __name__ == "__main__":
    main()
