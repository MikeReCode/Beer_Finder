""" Scraper that collects all the beers information from the Penny page """
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from .scraper import Scraper
from .scrapertools.tools import price_locator, convert_str_price_to_float, add_to_products


class PennyScraper(Scraper):

    link = "https://www.penny.ro/search/bere?tab=products"
    store = "Penny"
    all_products = dict()

    def __init__(self, driver):
        self.driver = driver
    
    def get_page_soup(self, page_link):
        # open the link in the browser
        self.driver.get(page_link)

        # click in the reject cookies button
        self.driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]').click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@class="caption"]')
            )
        )

        # extract HTML of the page
        page = self.driver.execute_script("return document.body.innerHTML")
        soup = BeautifulSoup("".join(page), "lxml")
        return soup

    def get_product_info(self, soup):
        # product information
        soap_info = soup.find_all(attrs={"data-teaser-group": "product"})
        # button that redirect to product page
        selenium_info = self.driver.find_elements(By.XPATH, '//*[@data-test="product-tile-link"]')
        info = zip(soap_info, selenium_info)
        return info
    
    def get_product_name(self, product):
        product_name = product.find("span", class_="show-sr-and-print").text.upper().strip()
        return product_name
    
    def get_product_price(self, product):
        product_price = product.find("div", class_="ws-product-price-type__value").text
        product_price = convert_str_price_to_float(price_locator(product_price))
        return product_price
    
    
    def get_price_per_liter(self, product):
        try:
            price_per_liter = product.find(
            "div", class_="caption"
            ).text.strip()
            price_per_liter = convert_str_price_to_float(price_locator(price_per_liter))
        except: # return None if the information was not found
            return None
        return price_per_liter

    def get_product_link(self, clickable):
        clickable.click()
        product_link = self.driver.current_url
        self.driver.find_element(By.XPATH, '//*[@data-test="dialog-close-btn"]').click()
        return product_link
       
    def store_product(self, product_name, price_per_liter, product_price, product_link):
        add_to_products(
            self.all_products,
            self.store,
            product_name,
            price_per_liter,
            product_price,
            product_link,
        )
    
    def run_scraper(self):
        soup = self.get_page_soup(self.link)
        info = self.get_product_info(soup)
        for product , clickable in info:
            product_name = self.get_product_name(product)
            product_price = self.get_product_price(product)
            price_per_liter = self.get_price_per_liter(product)
            product_link = self.get_product_link(clickable)
            self.store_product(product_name, price_per_liter, product_price, product_link)
        self.driver.quit()
        return self.all_products

if __name__ == '__main__':
    # to run the following code you have to delete the initial points of the last 2 imports at the beginning of the file
    #  from scraper import Scraper
    #  from scrapertools.tools import (price_locator, convert_str_price_to_float, add_to_products, calculate_liters)
    #
    # run the scraper individually (testing purposes)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(10)
    sc = PennyScraper(driver)
    penny_products = sc.run_scraper()

    for product in penny_products["products"]:
        print(product)
    print(len(penny_products["products"]))
