""" Scraper that collects all the beers information from the Auchan page """
from bs4 import BeautifulSoup
import requests

from .scraper import Scraper
from .scrapertools.tools import (
    price_locator,
    convert_str_price_to_float,
    add_to_products,
    calculate_liters,
    product_volume_locator,
)


class AuchanScraper(Scraper):

    link = "https://www.auchan.ro/store/Bere-si-cidru/c/u7t3c0s0000?q=%3Abestseller%3AproductStatuses%3AToate+produsele&page=0&pageSize=48&view=grid"
    store = "Auchan"
    all_products = dict()

    def get_page_soup(self, page_link):
        html_doc = requests.get(page_link).text
        soup = BeautifulSoup(html_doc, "lxml")
        return soup

    def get_product_info(self, soup):
        info = soup.find_all("div", class_="productListingPage")
        return info

    def get_product_name(self, product):
        product_name = product.find("h2", class_="details").text.upper().strip()
        return product_name

    def get_product_price(self, product):
        product_price = product.find("span", class_="big-price").text
        product_price = convert_str_price_to_float(price_locator(product_price))
        return product_price

    def get_price_per_liter(self, product_link, product_name, product_price):
        """
        Tries to calculate the price per liter through the product name and the price or by accessing the product page to
        retrieve the price per liter, however it can sometimes fail if the product name is more complex
        """

        def get_price_per_liter_accessig_product(product_link: str) -> float:
            """
            access the product to get the price per liter (this procedure is slower , thats why is used as a last resource )
            """
            soup = self.get_page_soup(product_link)
            price_per_liter = soup.find("p", class_="price-unit-value").text
            price_per_liter = convert_str_price_to_float(price_locator(price_per_liter))
            return price_per_liter

        try:
            # if can find the pattern of a pack with multiple products will access the product to get the price per liter
            calculate_liters(product_name, reverse_pattern=True)
            price_per_liter = get_price_per_liter_accessig_product(product_link)
        except: # if the pattern of a pack with multiple products is not found will just get the volume in liters of the product
                # to calculate the price per litter..
            try:
                volume_liters = product_volume_locator(product_name)
                if (
                    volume_liters > 10
                ):  # if the volume is too absurde access the product to get the price per liter
                    price_per_liter = get_price_per_liter_accessig_product(product_link)
                else:
                    # calculate price per liter
                    price_per_liter = round(product_price / volume_liters, 2)
            except:  # if its unable to locate the volume in liters of the product , just access the product to get the price per liter.
                price_per_liter = get_price_per_liter_accessig_product(product_link)
        return price_per_liter

    def get_product_link(self, product):
        product_link = "https://www.auchan.ro" + product.find(
            "a", attrs={"class": "productMainLink"}
        ).get("href")
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
        page = 0
        while next is not None:
            # extract HTML of the page
            soup = self.get_page_soup(
                f"https://www.auchan.ro/store/Bere-si-cidru/c/u7t3c0s0000?q=%3Abestseller%3AproductStatuses%3AToate+produsele&page={page}&pageSize=48&view=grid"
            )

            # find div that contain all the product information
            info = self.get_product_info(soup)

            # try to find if exists a next page with products
            next = soup.find("li", class_="last item")
            page += 1

            # extract product name and price per liter from the raw information
            for product in info:
                product_name = self.get_product_name(product)
                product_price = self.get_product_price(product)
                product_link = self.get_product_link(product)
                price_per_liter = self.get_price_per_liter(
                    product_link, product_name, product_price
                )
                self.store_product(
                    product_name, price_per_liter, product_price, product_link
                )
        nr_of_products = len(self.all_products["products"])
        print(f"{self.store} scrapper has finished !!  --  Nr of Products: {nr_of_products}")
        return self.all_products

if __name__ == '__main__':
    # to run the following code you have to delete the initial points of the last 2 imports at the beginning of the file
    #  from scraper import Scraper
    #  from scrapertools.tools import (price_locator, convert_str_price_to_float, add_to_products, calculate_liters)
    #
    # run the scraper individually (testing purposes)
    sc = AuchanScraper()
    auchan_products = sc.run_scraper()
    # auchan_products = sorted(auchan_products["products"], key=lambda x: x["price per liter"])  # in order to worck please use :   for product in auchan_products:    in the next loop

    for product in auchan_products["products"]:
        print(product)
    print(len(auchan_products["products"]))
