""" Scraper that collects all the beers information from the Altex page """
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from .scraper import Scraper
from .scrapertools.tools import (
    price_locator,
    convert_str_price_to_float,
    add_to_products,
    calculate_liters,
)


class AltexScraper(Scraper):

    link = "https://altex.ro/cauta/filtru/in-stoc-5182/in-stoc/?q=bere"
    store = "Altex"
    all_products = dict()

    def __init__(self, driver):
        self.driver = driver
    
    def get_page_soup(self, page_link):
        self.driver.get(page_link)
        page = self.driver.execute_script("return document.body.innerHTML")
        soup = BeautifulSoup("".join(page), "lxml")
        self.driver.quit()
        return soup

    def get_product_info(self, soup):
        info = soup.find_all("a", class_="Product")
        return info
    
    def get_product_name(self, product):
        product_name = product.find("h2", class_="Product-nameHeading").text.upper().strip()
        return product_name
    
    def get_product_price(self, product):
        product_price = product.find("div", class_="mt-auto").text.upper().strip()
        product_price = convert_str_price_to_float(price_locator(product_price))
        return product_price
    
    def get_price_per_liter(self, product):
        price = product.find("div", class_="mt-auto").text.upper().strip()
        price = convert_str_price_to_float(price_locator(price))
        liters = calculate_liters(self.get_product_name(product))
        price_per_liter = round(price / liters, 2)
        return price_per_liter

    def get_product_link(self, product):
        product_link = product.get("href")
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
            product_link = "https://altex.ro" + self.get_product_link(product)
            self.store_product(product_name, price_per_liter, product_price, product_link)

        nr_of_products = len(self.all_products["products"])
        print(f"{self.store} scrapper has finished !!  --  Nr of Products: {nr_of_products}")
        return self.all_products

if __name__ == '__main__':

    # to run the following code you have to delete the initial points of the last 2 imports at the beginning of the file
    #  from scraper import Scraper
    #  from scrapertools.tools import (price_locator, convert_str_price_to_float, add_to_products, calculate_liters)
    #
    # run the scraper individually (testing purposes)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(10)

    sc = AltexScraper(driver)
    altex_products = sc.run_scraper()

    for product in altex_products["products"]:
        print(product)
    print(len(altex_products["products"]))