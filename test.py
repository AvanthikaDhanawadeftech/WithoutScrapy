import requests
from bs4 import BeautifulSoup
import json
from tqdm import tqdm

list = []
def fetch_article_details(article_url):
    article_response = requests.get(article_url)
    dictionary = {}
    if article_response.status_code == 200:
        article_soup = BeautifulSoup(article_response.content, 'html.parser')
        h1_tag = article_soup.find('h1', class_='arttitle')
        h2_tag = article_soup.find('h2', class_='artdec')
        img_tag = article_soup.find('img', class_='lazy')
        dictionary["URL"] = article_url
        if h1_tag:
            dictionary["Title"] = h1_tag.text.strip()
            if h2_tag: 
                dictionary["Summary"] = h2_tag.text.strip()     
                if img_tag:
                    img_src = img_tag['src']
                    if img_src == "https://static.indiatvnews.com/ins-web/images/lazy-big.jpg":
                        dictionary.update({"Image URL": "Unable to fetch"})
                        dictionary["Image URL"] = "Unabel to fetch"
                        pass
                    else:
                        dictionary.update({"Image URL": img_src})
                        dictionary["Image URL"] = img_src
                        pass
                else:
                    print("No images found")
    else:
        print(f'Failed to retrieve the article. Status code: {article_response.status_code}')
        print("Article URL:", article_url)
    list.append(dictionary)
    

def scrape_and_fetch(link):
    response = requests.get(link)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        div_tag = soup.find('div', class_='row lhsBox sport_tnews mb20')

        if div_tag:
            thumb_links = div_tag.find_all('a', class_='thumb')

            for thumb_link in thumb_links:
                article_url = thumb_link.get('href')
                fetch_article_details(article_url)
        else:
            print('Failed to find the div with class="row lhsBox sport_tnews mb20".')
    else:
        print(f'Failed to retrieve the webpage. Status code: {response.status_code}')
        print("scrape_and_fetch", link)


def scrape_and_fetch2(link):
    response = requests.get(link)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        div_tag = soup.find('div', class_='row lhsBox s_two_column pt20')

        if div_tag:
            thumb_links = div_tag.find_all('a', class_='thumb')

            for thumb_link in thumb_links:
                article_url = thumb_link.get('href')
                fetch_article_details(article_url)
        else:
            print('Failed to find the div with class="row lhsBox s_two_column pt20".')
    else:
        print(f'Failed to retrieve the webpage. Status code: {response.status_code}')
        print("scrape_and_fetch2", link)


def scrape_and_fetch3(link):
    response = requests.get(link)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        li_tags = soup.find_all('li', class_='p_news eventTracking')

        for li_tag in li_tags:
            thumb_links = li_tag.find_all('a', class_='thumb')

            for thumb_link in thumb_links:
                article_url = thumb_link.get('href')
                fetch_article_details(article_url)

        next_page_link = soup.find('a', class_='pnnext')

        if next_page_link:
            next_page_url = next_page_link.get('href')
            scrape_and_fetch3(next_page_url)
    else:
        print(f'Failed to retrieve the webpage. Status code: {response.status_code}')
        print("scrape_and_fetch3", link)

def scrape_and_fetch4(link):
    response = requests.get(link)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # First part: div tag with class="lhsBox top-news-list-election mb5 row"
        div_tag1 = soup.find('div', class_='lhsBox top-news-list-election mb5 row')
        if div_tag1:
            big_news_div = div_tag1.find('div', class_='big-news eventTracking')
            if big_news_div:
                a_tag = big_news_div.find('a')
                if a_tag:
                    article_url = a_tag.get('href')
                    fetch_article_details(article_url)
                
        
        # Second part: div tag with class="big-news-list"
        div_tag2 = soup.find('div', class_='big-news-list')
        if div_tag2:
            li_tags = div_tag2.find_all('li')
            for li_tag in li_tags:
                a_tag = li_tag.find('a')
                if a_tag:
                    article_url = a_tag.get('href')
                    fetch_article_details(article_url)            
    else:
        print(f'Failed to retrieve the webpage. Status code: {response.status_code}')
        print("scrape_and_fetch4", link)

def main():
    url = 'https://www.indiatvnews.com/'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        ul_tag = soup.find('ul', class_='menu megamenu')
        
        links = []

        if ul_tag:
            a_tags = ul_tag.find_all('a')
            links = [a_tag.get('href') for a_tag in a_tags[2:-1] if a_tag.get('href')]
        else:
            print('Failed to find the ul with class="menu megamenu".')

        # Define the indices of the links to use
        indices_to_use = [8, 9, 10, 11, 12, 13, 15, 17, 22]
        other_indices_to_use = [4, 7, 14, 18, 20, 21, 23, 25] 
        # Iterate over the indices and use corresponding links
        for index in tqdm(indices_to_use, desc="Processing Links"):
            link = links[index]
            scrape_and_fetch(link)
            scrape_and_fetch2(link)
            scrape_and_fetch3(link)
            # scrape_and_fetch4(link)
        print(len(list))
        for index in tqdm(other_indices_to_use, desc="Processing Links"):
            link = links[index]
            scrape_and_fetch4(link)
            scrape_and_fetch2(link)
            scrape_and_fetch3(link)
        
        print(len(list))
        with open("data2.json", "w") as json_file:
        # Write the list to the JSON file
            json.dump(list, json_file, indent=4)
    else:
        print(f'Failed to retrieve the webpage. Status code: {response.status_code}')

if __name__ == "__main__":
    main()
