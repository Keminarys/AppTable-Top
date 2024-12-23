from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os

# Set up the WebDriver
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# Open the login page
driver.get("https://boardgamegeek.com/login")

# Wait until the username input field is clickable and enter username and password
wait = WebDriverWait(driver, 10)
wait.until(EC.element_to_be_clickable((By.ID, 'inputUsername'))).send_keys(username)
driver.find_element(By.ID, 'inputPassword').send_keys(password)

# Submit the form
driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

# Wait for login to be successful
wait.until(EC.url_changes("https://boardgamegeek.com/login"))

# Function to scrape page data
def scrape_page(page_number):
    driver.get(f"{url_base}{page_number}")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.find_all('tr', {'id': lambda x: x and x.startswith('row_')})
    
    for row in rows:
        game_name = row.find('a', class_='primary').text.strip() if row.find('a', class_='primary') else 'None'
        description_short = row.find('p', class_='smallefont dull').text.strip() if row.find('p', class_='smallefont dull') else 'None'
        geek_rating = float(row.find('td', {'class': 'collection_bggrating'}).text.strip()) if row.find('td', {'class': 'collection_bggrating'}) else 0
        avg_rating = float(row.find_all('td', {'class': 'collection_bggrating'})[1].text.strip()) if len(row.find_all('td', {'class': 'collection_bggrating'})) > 1 else 0
        url = row.find('a', class_='primary')['href'] if row.find('a', class_='primary') else 'None'
        
        games.append([game_name, description_short, geek_rating, avg_rating, url])

# Now scrape the page
url_base = "https://boardgamegeek.com/browse/boardgame/page/"
games = []

# Get the content of the first page to find the number of pages
driver.get(url_base + "1")
soup = BeautifulSoup(driver.page_source, 'html.parser')
pagination = soup.find('div', {'class': 'fr'})
last_page_link = pagination.find('a', {'title': 'last page'})
last_page_number = int(last_page_link['href'].split('/')[-1])

# Scrape all pages
for i in range(1, last_page_number + 1): 
  scrape_page(i)

# Create the DataFrame
df = pd.DataFrame(games, columns=["GameName", "DescriptionShort", "GeekRating", "AvgRating", "url"])

# Close the browser
driver.quit()

#Save DF as a pickle file 
df.to_pickle('games.pkl')
