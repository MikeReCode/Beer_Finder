""" Scraper that collects all the beers information from the Emag page """
from bs4 import BeautifulSoup
import requests

from .scraper import Scraper
from .scrapertools.tools import price_locator, convert_str_price_to_float, add_to_products


class EmagScraper(Scraper):

    link = "https://www.emag.ro/search/beri/stoc/bere/c?ref=lst_leftbar_6407_stock"
    store = "Emag"
    all_products = dict()

    def get_page_soup(self, page_link):
        html_doc = requests.get(page_link).text
        soup = BeautifulSoup(html_doc, "lxml")
        return soup

    def get_product_info(self, soup):
        info = soup.find_all("div", class_="card-v2")
        return info

    def get_product_name(self, product):
        product_name = product.find("a", class_="card-v2-title").text.upper().strip()
        return product_name

    def get_product_price(self, product):
        product_price = product.find("p", class_="product-new-price").text
        product_price = convert_str_price_to_float(price_locator(product_price))
        return product_price

    def get_price_per_liter(self, product):
        price_per_liter = product.find("p", class_="legal-price-label").text 
        price_per_liter = convert_str_price_to_float(price_locator(price_per_liter))
        return price_per_liter

    def get_product_link(self, product):
        product_link = product.find("a", attrs={"data-zone": "thumbnail"}).get("href")  # type: ignore
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
        while next is not None:
            # extract HTML of the page
            if next == "":
                soup = self.get_page_soup(self.link)
            else:
                soup = self.get_page_soup("https://www.emag.ro" + next)

            # find div that contain all the product information
            info = self.get_product_info(soup)

            # try to find if exists a next page with products
            try:
                next = soup.find("a", class_="js-next-page")
                next = next.get("href")
            except:
                pass  # no more pages for this products

            # extract product name and price per liter from the raw information
            for product in info:
                try:
                    product_name = self.get_product_name(product)
                    price_per_liter = self.get_price_per_liter(product)
                    product_price = self.get_product_price(product)
                    product_link = self.get_product_link(product)
                    self.store_product(
                        product_name, price_per_liter, product_price, product_link
                    )

                except Exception as e: 
                    pass # if one of the information is not found, go to the next product

        nr_of_products = len(self.all_products["products"])
        print(f"{self.store} scrapper has finished !!  --  Nr of Products: {nr_of_products}")
        return self.all_products

if __name__ == '__main__':
    # to run the following code you have to delete the initial points of the last 2 imports at the beginning of the file
    #  from scraper import Scraper
    #  from scrapertools.tools import (price_locator, convert_str_price_to_float, add_to_products, calculate_liters)
    #
    # run the scraper individually (testing purposes)
    sc = EmagScraper()
    emag_products = sc.run_scraper()

    for product in emag_products["products"]:
        print(product)
    print(len(emag_products["products"]))
