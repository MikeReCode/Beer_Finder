""" Scraper that collects all the beers information from the Freshful page (page only for bucharest) """
import requests
from bs4 import BeautifulSoup

from .scraper import Scraper
from .scrapertools.tools import price_locator, convert_str_price_to_float, add_to_products


class FreshfulScraper(Scraper):

    link = "https://www.freshful.ro/c/7-bauturi-si-tutun/704-bere"
    store = "Freshful"
    all_products = dict()

    def get_page_soup(self, page_link):
        html_doc = requests.get(page_link).text
        soup = BeautifulSoup(html_doc, "lxml")
        return soup

    def get_product_info(self, soup):
        info = soup.find_all("a", attrs={'class': lambda x: x.startswith('ProductCard_root') if x else False})
        return info

    def get_product_name(self, product):
        brand_name = product.find("div", attrs={'class': lambda x: x.startswith('ProductCard_brand') if x else False}).text.upper().strip()
        type_beer = product.find("div", attrs={'class': lambda x: x.startswith('ProductCard_name') if x else False}).text.upper().strip()
        product_name = f"{brand_name} {type_beer}"
        return product_name

    def get_product_price(self, product):
        try:
            product_price = product.find("div", attrs={'class': lambda x: x.startswith('ProductCard_currentPrice') if x else False}).text.upper().strip()
            product_price = convert_str_price_to_float(price_locator(product_price))
            return product_price
        except: # return None if the information was not found
            return None

    def get_price_per_liter(self, product):
        try:
            price_per_liter = product.find("div", attrs={'class': lambda x: x.startswith('ProductCard_unitPriceLabelText') if x else False}).text
            price_per_liter = convert_str_price_to_float(price_locator(price_per_liter, int_price=True))
            return price_per_liter
        except: # return None if the information was not found
            return None

    def get_product_link(self, product):
        product_link = "https://www.freshful.ro" + product.get("href")
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
        next = ""
        next_page = ""
        page = 1

        while next_page is not None:
            soup = self.get_page_soup(self.link + next)
            info = self.get_product_info(soup)

            # try to find if exists a next page with products
            next_page = soup.find("li", class_="pagination-next-page").find(attrs={"aria-disabled": "false"})
            page +=1
            # suffix to compleet the next page link
            next = f"/p{page}"

            # extract product name and price per liter from the raw information
            for product in info:
                product_name = self.get_product_name(product)
                price_per_liter = self.get_price_per_liter(product)
                product_price = self.get_product_price(product)
                product_link = self.get_product_link(product)
                self.store_product(
                    product_name, price_per_liter, product_price, product_link
                )

        return self.all_products

        
if __name__ == '__main__':
    # to run the following code you have to delete the initial points of the last 2 imports at the beginning of the file
    #  from scraper import Scraper
    #  from scrapertools.tools import (price_locator, convert_str_price_to_float, add_to_products, calculate_liters)
    #
    # run the scraper individually (testing purposes)
    sc = FreshfulScraper()
    freshful_products = sc.run_scraper()

    for product in freshful_products["products"]:
        print(product)
    print(len(freshful_products["products"]))