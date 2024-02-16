# Tor Crawler with PostgreSQL Integration

This Python script allows you to crawl onion links using the Tor network and store the crawled data into a PostgreSQL database.

## Prerequisites

- Python 3.x
- `requests`, `stem`, `bs4` (Beautiful Soup), and `psycopg2` Python libraries
- Tor installed and running
- PostgreSQL installed and running

## Installation

1. Clone this repository or download the script file.
2. Install the required Python libraries:
3. Ensure Tor is running on your system.

## Configuration

- Set the `num_links_to_crawl` variable to specify the number of links to crawl.
- Set the `user_agent` variable to define the user agent for the requests.
- Update the Tor controller port and password if needed.
- Modify the PostgreSQL connection parameters (`dbname`, `user`, `password`, `host`, `port`) as per your database configuration.

## Usage

1. Run the script:
2. Enter a list of keywords to search for when prompted.
3. The script will start crawling onion links, storing the title and URL of each page in the PostgreSQL database.
4. Once the specified number of links (`num_links_to_crawl`) is reached, or there are no more links to crawl, the script will stop.

## Output

- Crawled data (title and URL) will be stored in the `crawled_data` table in the PostgreSQL database.
- Visited links will be printed at the end of the script execution.

## License

This project is licensed under the [MIT License](LICENSE).
