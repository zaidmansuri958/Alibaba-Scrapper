import time
import numpy as np 
import pandas as pd 
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ElectronicScrapper:
    def __init__(self,url,timeout=10):
        self.url=url
        self.data=[]
        self.driver=self.initialize_driver()
        self.wait=WebDriverWait(self.driver,timeout=timeout)

    def initialize_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-http2")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument(
            "--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument(
            "--enable-features=NetworkServiceInProcess")
        chrome_options.add_argument("--disable-features=NetworkService")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
        )
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-web-security")
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        return driver

    def wait_for_page_to_load(self):
        title = self.driver.title
        try:
            self.wait.until(
                lambda d: d.execute_script(
                    "return document.readyState") == "complete"
            )
        except:
            print(f"the webpage {title} did not fully loaded")
        else:
            print(f"The page {title} fully loaded")
        
    def access_website(self):
        self.driver.get(self.url)
        self.wait_for_page_to_load()

    def search_electronics(self,text):
        try:
            search_bar=self.wait.until(
                EC.presence_of_element_located((By.XPATH,'//*[@id="root"]/div[1]/div[3]/div/div[3]/div/div/div[1]/div[1]/input'))
            )
        except:
            print("Timeout while locating search bar")
        else:
            search_bar.send_keys(text)
            time.sleep(2)

        try:
            search_button=self.wait.until(
                EC.element_to_be_clickable((By.XPATH,"/html[1]/body[1]/div[1]/div[1]/div[3]/div[1]/div[3]/div[1]/div[1]/div[1]/button[1]/img[1]"))
            )
        except:
            print("Time out while finding search button")
        else:
            search_button.click()
            self.wait_for_page_to_load()

    
    def navigate_pages_and_scrap(self):
        page_count=0
        while True:
            page_count+=1
            try:
                self.scrape_webpage()
                next_page_btn=self.driver.find_element(
                    By.XPATH,'//*[@id="content-footer"]/div[1]/div/a[2]/button'
                )
            except:
                print(f"We have scraped {page_count} pages")
                break 
            else:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_page_btn)
                    time.sleep(2)
                    self.driver.execute_script(
                        "window.scrollBy(0, arguments[0].getBoundingClientRect().top - 100);", next_page_btn)
                    time.sleep(2)
                    self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="content-footer"]/div[1]/div/a[2]/button'))).click()
                    time.sleep(5)
                except:
                    print("Timeout while clicking on \"Next Page\".\n")

    def scrape_webpage(self):
                cards = self.driver.find_elements(By.CLASS_NAME, "fy23-search-card")
                for card in cards:
                    try:
                        # Title
                        title_element = card.find_element(By.CSS_SELECTOR, "h2.search-card-e-title span")
                        title = title_element.text

                        # Product URL
                        product_url = card.find_element(By.CSS_SELECTOR, "h2.search-card-e-title a").get_attribute("href")

                        # Image URL
                        img_element = card.find_element(By.CSS_SELECTOR, "img.search-card-e-slider__img")
                        image_url = img_element.get_attribute("src")

                        # Price
                        price = card.find_element(By.CSS_SELECTOR, ".search-card-e-price-main").text

                        # Min. Order
                        min_order = card.find_element(By.CSS_SELECTOR, ".search-card-m-sale-features__item").text

                        # Company
                        company = card.find_element(By.CSS_SELECTOR, ".search-card-e-company").text

                        # Rating and reviews
                        try:
                            review_span = card.find_element(By.CSS_SELECTOR, "span.search-card-e-review")
                            rating_text = review_span.text
                        except:
                            print("Review Score not found on this page.")
                        item={
                            "title":title,
                            "product_url":product_url,
                            "image_url":image_url,
                            "price":price,
                            "min_order":min_order,
                            "company":company,
                            "rating_text":rating_text

                        }
                        self.data.append(item)
                    except Exception as e:
                        print("Failed to extract one of the elements:", e)
        
    def save_data(self):
        df=pd.DataFrame(self.data)
        df.to_excel("electronic_data.xlsx",index=False)

    def run(self,text):
        try:
            self.access_website()
            self.search_electronics(text)
            self.navigate_pages_and_scrap()
            self.save_data()
        finally:
            time.sleep(2)
            self.driver.quit()
if __name__ == "__main__":
    scrapper=ElectronicScrapper(url="https://www.alibaba.com/")
    scrapper.run("electronics")