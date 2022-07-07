""" Scraper that collects all the beers information from the MegaImage page """
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

import time

from .scraper import Scraper
from .scrapertools.tools import price_locator, convert_str_price_to_float, add_to_products



class MegaImageScraper(Scraper):

    link = "https://www.mega-image.ro/Bauturi-si-tutun/Bere-si-Cidru/c/009001?q=%3Arelevance&sort=relevance"
    store = "Mega Image"
    all_products = dict()

    def __init__(self, driver):
        self.driver = driver

    def get_page_soup(self, page_link):
        self.driver.get(page_link)
        # click in the reject cookies button
        self.driver.find_element(By.XPATH, '//*[@data-testid="cookie-popup-reject"]').click()
        # scroll down until reach the bottom of the page , this allow to load all products in the page
        height = self.driver.execute_script("return document.documentElement.scrollHeight")
        self.driver.execute_script("document.body.style.zoom='50%'")
        while True:
            html = self.driver.find_element(By.TAG_NAME, "html")
            html.send_keys(Keys.END)
            time.sleep(3)
            new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == height:
                break
            height = new_height

        # extract HTML of the page
        page = self.driver.execute_script("return document.body.innerHTML")
        soup = BeautifulSoup("".join(page), "lxml")
        self.driver.quit()
        return soup


    def get_product_info(self, soup):
        info = soup.find_all(attrs={"data-testid": "product-block"})
        return info
    
    def get_product_name(self, product):
        brand_name = (
        product.find(attrs={"data-testid": "product-block-brand-name"}).text.upper().strip()
        )
        type_beer = (
        product.find(attrs={"data-testid": "product-block-product-name"}).text.upper().strip()
        )
        product_name = f"{brand_name} {type_beer}"
        return product_name
    
    def get_product_price(self, product):
        try:
            product_price = (
                product.find(attrs={"data-testid": "product-block-price"})
                .text.upper()
                .strip()
            )
            product_price = convert_str_price_to_float(price_locator(product_price))
            return product_price
        except: # return None if the information was not found
            return None
            
    def get_price_per_liter(self, product):
        try:
            price_per_liter = (
                product.find(attrs={"data-testid": "product-block-price-per-unit"})
                .text.upper()
                .strip()
            )
            price_per_liter = convert_str_price_to_float(price_locator(price_per_liter))
            return price_per_liter
        except: # return None if the information was not found
            return None

    def get_product_link(self, product):
        product_link = "https://www.mega-image.ro" + product.find(attrs={"data-testid": "product-block-image-link"}).get("href")
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

        for product in info:
            product_name = self.get_product_name(product)
            product_price = self.get_product_price(product)
            price_per_liter = self.get_price_per_liter(product)
            product_link = self.get_product_link(product)
            self.store_product(product_name, price_per_liter, product_price, product_link)

        return self.all_products

if __name__ == '__main__':
    # to run the following code you have to delete the initial points of the last 2 imports at the beginning of the file
    #  from scraper import Scraper
    #  from scrapertools.tools import (price_locator, convert_str_price_to_float, add_to_products, calculate_liters)
    #
    # run the scraper individually (testing purposes)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(10)

    sc = MegaImageScraper(driver)
    megaimage_products = sc.run_scraper()

    for product in megaimage_products["products"]:
        print(product)
    print(len(megaimage_products["products"]))