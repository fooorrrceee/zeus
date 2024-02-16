import pandas as pd
import psycopg2
import random
import requests
import bs4
from collections import OrderedDict

def ingest_google_news():
    query = 'financial cyber-threat'        
    url = f"https://www.google.com/search?q={query}&tbm=nws&lr=lang_en&hl=en&sort=date&num=5"

    df = pd.DataFrame()
    t_news = []
    t_publisher = []
    t_urls = []
    t_dates =  []

    # set header by random user agent.
    r = requests.Session()
    headers = random_header()
    r.headers = headers

    res = r.get(url, headers=headers)
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    
    links = soup.select(".dbsr a")
    for l in links:
        try:
            url_w = l.get("href")
            t_urls.append(url_w)
            dt = find_date(url_w)
            t_dates.append(dt)

            res = requests.get(url_w, headers=headers)
            parsed_article = bs4.BeautifulSoup(res.text,'lxml')
            paragraphs = parsed_article.find_all('p')

            article_text = ""
            for p in paragraphs:
                article_text += p.text

            t_news.append(article_text)
        except Exception as e:
            print(f"Error processing URL: {url_w}. Error: {str(e)}")

    # Parsing publishers
    sources = soup.select(".XTjFC span")
    for s in sources:
        t_publisher.append(s.get_text().lower())

    df['links'] = t_urls
    df['article_text'] = t_news
    df['publisher'] = t_publisher
    df['created_at'] = t_dates

    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        dbname="zeus",       
        user="postgres",
        password="inr_db",
        host="db.inr.intellx.in",
        port="5432"
    )

    # Append data to database table
    df.to_sql('gnews', conn, if_exists='append', index=False)

    # Close database connection
    conn.close()

def list_header():
    headers_list = [
        # Firefox 24 Linux
        {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        # Firefox Mac
        {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    ]
    
    return headers_list

def list_dict():
    # Get headers list
    headers_list = list_header()
    # Create ordered dict from Headers above
    ordered_headers_list = []
    for headers in headers_list:
        h = OrderedDict()
        for header,value in headers.items():
            h[header]=value
        ordered_headers_list.append(h)
    return ordered_headers_list

def list_test():
    headers_list = list_dict()
    max = len(headers_list)
    url = 'https://httpbin.org/headers'
    for i in range(0,max):
        #Pick a random browser headers
        headers = random.choice(headers_list)
        #Create a request session
        r = requests.Session()
        r.headers = headers
        
        response = r.get(url)
        print("Request #%d\nUser-Agent Sent:%s\n\nHeaders Recevied by HTTPBin:"%(i,headers['User-Agent']))
        print(response.json())
        print("-------------------")

def random_header():
    headers_list = list_dict()
    headers = random.choice(headers_list)
    return headers


    
def find_date(url):
    headers = random_header()
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    
    # Check if the date is available in the search result snippet
    date_element = soup.find("span", class_="hvbAAd")
    if date_element:
        return date_element.text.strip()

    # If date is not available in the snippet, try to find it within the news article
    article_links = soup.select(".dbsr a")
    for link in article_links:
        article_url = link.get("href")
        article_res = requests.get(article_url)
        article_soup = bs4.BeautifulSoup(article_res.text, "html.parser")
        date_element = article_soup.find("time")  # Assuming date is in a <time> element
        if date_element:
            return date_element.text.strip()

    # If date cannot be found, return None
    return None
ingest_google_news()
