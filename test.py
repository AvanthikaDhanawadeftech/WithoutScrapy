import requests
from bs4 import BeautifulSoup
import json
from tqdm import tqdm
import os

parsed_results = []
visited_articles = []

def parse_the_link(link):
    if link in visited_articles:
        return None
    visited_articles.append(link)
    response = requests.get(link)
    if response.status_code == 200:
        html_content = response.content
        file_name = link.split('/')[-1] + '.html'  # Extract filename from URL
        file_path = os.path.join('html_files', file_name)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save HTML content to file
        with open(file_path, 'wb') as file:
            file.write(html_content)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    else:
        print(f'Failed to retrieve the webpage. Status code: {response.status_code}')
        print("scrape_and_fetch", link)
        return None

def fetch_article_details(parsed_article):
    article_soup = parse_the_link(parsed_article)
    if article_soup == None:
        return None

    dictionary = {}
    dictionary["URL"] = parsed_article
    h1_tag = article_soup.find('h1', class_='arttitle')
    h2_tag = article_soup.find('h2', class_='artdec')
    img_tag = article_soup.find('img', class_='lazy')

    if h1_tag:
        dictionary["Title"] = h1_tag.text.strip()
        if h2_tag: 
            dictionary["Summary"] = h2_tag.text.strip()     
            if img_tag:
                img_src = img_tag['data-original']
                if img_src == "https://static.indiatvnews.com/ins-web/images/lazy-big.jpg":
                    dictionary.update({"Image URL": "Unable to fetch"})
                else:
                    dictionary.update({"Image URL": img_src})
            else:
                print("No images found")   
    parsed_results.append(dictionary)

def scrape_and_fetch(link, div_class, soup):
    div_tag = soup.find('div', class_=div_class)
    if div_tag:
        thumb_links = div_tag.find_all('a', class_='thumb')
        for thumb_link in thumb_links:
            parsed_article = thumb_link.get('href')
            fetch_article_details(parsed_article)
    else:
        print(f'Failed to find the div with class={div_class}')

def scrape_and_fetch4(link, soup):
    div_tag1 = soup.find('div', class_='lhsBox top-news-list-election mb5 row')
    if div_tag1:
        big_news_div = div_tag1.find('div', class_='big-news eventTracking')
        if big_news_div:
            a_tag = big_news_div.find('a')
            if a_tag:
                parsed_article = a_tag.get('href')
                fetch_article_details(parsed_article)
    div_tag2 = soup.find('div', class_='big-news-list')
    if div_tag2:
        li_tags = div_tag2.find_all('li')
        for li_tag in li_tags:
            a_tag = li_tag.find('a')
            if a_tag:
                parsed_article = a_tag.get('href')
                fetch_article_details(parsed_article)

def scrape_and_fetch3(link, soup):
    li_tags = soup.find_all('li', class_='p_news eventTracking')
    for li_tag in li_tags:
        thumb_links = li_tag.find_all('a', class_='thumb')
        for thumb_link in thumb_links:
            parsed_article = thumb_link.get('href')
            fetch_article_details(parsed_article)

    next_page_link = soup.find('a', class_='pnnext')
    if next_page_link:
        next_page_url = next_page_link.get('href')
        soup = parse_the_link(next_page_url)
        if soup == None:
            return None
        scrape_and_fetch3(next_page_url, soup)

def main():
    soup = parse_the_link('https://www.indiatvnews.com/')
    if soup == None:
        return None

    ul_tag = soup.find('ul', class_='menu megamenu')
    links = []

    if ul_tag:
        a_tags = ul_tag.find_all('a')
        links = [a_tag.get('href') for a_tag in a_tags[2:-1] if a_tag.get('href')]
    else:
        print('Failed to find the ul with class="menu megamenu".')

    # print(len(links))
    for link in tqdm(links, desc="Processing Links"):
        # print(len(parsed_results))
        soup = parse_the_link(link)
        if soup == None:
            continue
        div1 = soup.find('div', class_='row lhsBox sport_tnews mb20')
        div2 = soup.find('div', class_='row lhsBox s_two_column pt20')
        div3 = soup.find('div', class_='lhsBox top-news-list-election mb5 row')
        div4 = soup.find('div', class_='topNews row mb30')

        if div1:
            scrape_and_fetch(link, 'row lhsBox sport_tnews mb20', soup)
        if div2:
            scrape_and_fetch(link, 'row lhsBox s_two_column pt20', soup)
        if div3:
            scrape_and_fetch4(link, soup)
        if div4:
            scrape_and_fetch3(link, soup)

    print(len(parsed_results))

    with open("data.json", "w") as json_file:
        json.dump(parsed_results, json_file, indent=4)
    print("JSON file created successfully.")

if __name__ == "__main__":
    main()
