import time
import requests
from stem import Signal
from stem.control import Controller
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Set the number of links to crawl
num_links_to_crawl = 10

# Set the user agent to use for the request
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'

# Set the headers for the request
headers = {'User-Agent': user_agent}

# Define the SQLAlchemy model
Base = declarative_base()

class CrawledData(Base):
    __tablename__ = 'crawled_data'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)

# Initialize the controller for the Tor network
with Controller.from_port(port=9051) as controller:
    # Set the controller password
    controller.authenticate(password='16:700C7086C99090B260181CB34A53106EE1C04B5B06B70AB9433BE10E6F')

    # Set the starting URL
    url = 'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q=bank+data+leak'
    # Initialize the visited set and the link queue
    visited = set()
    queue = [url]

    # Get the list of keywords to search for
    keywords = ('bank', 'data', 'leak')

    # Connect to the PostgreSQL database using SQLAlchemy
    db_url = 'postgresql://postgres:inr_db@db.inr.intellx.in:5432/zeus'
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create the table if it does not exist
    Base.metadata.create_all(engine)

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
        try:
            response = requests.get(link, headers=headers)
        except requests.RequestException as e:
            print(f"Error fetching {link}: {e}")
            continue

        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find title of the page
        title = soup.title.string.strip()

        # Insert title and URL into the database
        try:
            data = CrawledData(title=title, url=link)
            session.add(data)
            session.commit()
        except Exception as e:
            session.rollback()  # Rollback transaction if insertion fails
            print(f"Error inserting {title}, {link} into database: {e}")

        # Find all links on the page
        links = soup.find_all('a')

        # Add any links that contain the keywords to the queue
        for a in links:
            href = a.get('href')
            if href and any(keyword in href for keyword in keywords):
                queue.append(href)

        # Add the link to the visited set
        visited.add(link)

        # Print the title and URL of the page
        print(title, link)

        # Check if the number of visited links has reached the limit
        if len(visited) >= num_links_to_crawl:
            break

    # Close session
    session.close()

# Print the visited links
print('Visited links:')
for link in visited:
    print(link)
