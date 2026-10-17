from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# =============================
# SETTINGS
# =============================
cities = [
    "Lahore", "Karachi", "Islamabad",
    "Multan", "Peshawar", "Faisalabad",
    "Sahiwal", "Okara", "Bahawalpur"
]

search_term = "cattle farmer"
excel_file = "C:\Users\RABIA\Desktop\scrapping\cattle_farmers_pakistan.xlsx"

# =============================
# DRIVER SETUP
# =============================
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 15)
results = []

# =============================
# SCRAPE FUNCTION
# =============================
def scrape_city(city):
    driver.get("https://www.google.com/maps")

    search = wait.until(
        EC.presence_of_element_located((By.ID, "searchboxinput"))
    )
    search.clear()
    search.send_keys(f"{search_term} in {city}")
    search.send_keys(Keys.ENTER)

    time.sleep(6)

    try:
        scrollable = wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
        )
    except:
        print(f"No results feed for {city}")
        return

    last_height = 0

    # -------- SCROLL UNTIL END --------
    while True:
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight",
            scrollable
        )
        time.sleep(3)

        new_height = driver.execute_script(
            "return arguments[0].scrollHeight",
            scrollable
        )
        if new_height == last_height:
            break
        last_height = new_height

    listings = driver.find_elements(
        By.XPATH, '//a[contains(@href,"/place/")]'
    )

    print(f"{city}: {len(listings)} cattle farmers found")

    place_links = list(set(
        [l.get_attribute("href") for l in listings]
    ))

    # -------- OPEN EACH PLACE --------
    for link in place_links:
        driver.get(link)
        time.sleep(4)

        try:
            name = driver.find_element(By.XPATH, '//h1').text
        except:
            name = "N/A"

        try:
            address = driver.find_element(
                By.XPATH, '//button[@data-item-id="address"]'
            ).text
        except:
            address = "N/A"

        try:
            phone = driver.find_element(
                By.XPATH, '//button[contains(@data-item-id,"phone")]'
            ).text
        except:
            phone = "N/A"

        results.append({
            "City": city,
            "Farmer / Farm Name": name,
            "Address": address,
            "Phone": phone,
            "Google Maps Link": link
        })

# =============================
# RUN
# =============================
for city in cities:
    print(f"🔍 Scraping cattle farmers in {city}")
    scrape_city(city)

# =============================
# SAVE TO EXCEL
# =============================
df = pd.DataFrame(results).drop_duplicates()
df.to_excel(excel_file, index=False)

print(f"✅ Saved {len(df)} records to {excel_file}")

driver.quit()
