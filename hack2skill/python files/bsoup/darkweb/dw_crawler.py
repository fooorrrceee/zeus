import time
import requests
from stem import Signal
from stem.control import Controller
from bs4 import BeautifulSoup
import psycopg2

# Set the number of links to crawl
num_links_to_crawl = 100

# Set the user agent to use for the request
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'

# Set the headers for the request
headers = {'User-Agent': user_agent}

# Initialize the controller for the Tor network
with Controller.from_port(port=9051) as controller:
    # Set the controller password
    controller.authenticate(password='mypassword')

    # Set the starting URL
    url = 'https://27m3p2uv7igmj6kvd4ql3cct5h3sdwrsajovkkndeufumzyfhlfev4qd.onion/'

    # Initialize the visited set and the link queue
    visited = set()
    queue = [url]

    # Get the list of keywords to search for
    keywords = input('Enter a list of keywords to search for, separated by commas: ').split(',')

    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        dbname="zeus",       
        user="postgres",
        password="inr_db",
        host="db.inr.intellx.in",
        port="5432"
    )
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("CREATE TABLE IF NOT EXISTS crawled_data (id SERIAL PRIMARY KEY, title TEXT, url TEXT)")

    # Commit changes
    conn.commit()

    # Crawl the links
    while queue:
        # Get the next link in the queue
        link = queue.pop(0)

        # Skip the link if it has already been visited
        if link in visited:
            continue

        # Set the new IP address
        controller.signal(Signal.NEWNYM)

        # Send the request to the URL
        response = requests.get(link, headers=headers)

        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find title of the page
        title = soup.title.string.strip()

        # Insert title and URL into the database
        cursor.execute("INSERT INTO crawled_data (title, url) VALUES (%s, %s)", (title, link))
        conn.commit()

        # Find all links on the page
        links = soup.find_all('a')

        # Add any links that contain the keywords to the queue
        for a in links:
            href = a.get('href')
            if any(keyword in href for keyword in keywords):
                queue.append(href)

        # Add the link to the visited set
        visited.add(link)

        # Print the title and URL of the page
        print(title, link)

        # Check if the number of visited links has reached the limit
        if len(visited) >= num_links_to_crawl:
            break

    # Close cursor and connection
    cursor.close()
    conn.close()

# Print the visited links
print('Visited links:')
for link in visited:
    print(link)
