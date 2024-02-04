from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import json
import psycopg2


conn = psycopg2.connect(
    dbname="zeus",
    user="postgres",
    password="inr_db",
    host="db.inr.intellx.in",
    port="5432"
)

cur = conn.cursor()


chromedriver_path="/Applications/chromedriver-mac-x64/chromedriver"
url = 'https://www.google.com/search?sca_esv=37f724872de16756&q=financial+cyber+threat+news&tbm=nws&source=lnms&sa=X&ved=2ahUKEwjN3qK9spGEAxUqwTgGHTMmCUsQ0pQJegQIDBAB&biw=1200&bih=933&dpr=2'
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)
driver.get(url)

news_results = driver.find_elements(By.CSS_SELECTOR, 'div#rso > div > div > div > div')
for news_div in news_results:
    news_item = []
    try:
        news_link = news_div.find_element(By.TAG_NAME, 'a').get_attribute('href')
        print("Link:", news_link)

        divs_inside_news = news_div.find_elements(By.CSS_SELECTOR, 'a > div > div > div')
        id =0
        for new in divs_inside_news:
            news_item.append(new.text)
            item_dict = dict(domain = news_item[1], title = news_item[2], description = news_item[3],date=news_item[4])
            cur.execute('INSERT INTO  (item_id,domain, title, description,time) VALUES (&s,&s,&s , &s, &s , &s)', (i+1,news_item[1], , news_item[2],news_item[3] , news_item[4]))
            conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
driver.quit()
