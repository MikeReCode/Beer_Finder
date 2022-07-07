""" All the functions necessary for the scraper to work """
import re
from typing import Union


def add_to_products(
    products: dict,
    store: str,
    product_name: str,
    price_per_liter: Union[float, None],
    product_price: Union[float, None],
    product_link: str,
) -> None:
    """
    Add product to a given dictionary
    """
    if len(products) == 0:
        products["products"] = list()
    if price_per_liter is not None and product_price is not None:
        products["products"].append(
            {
                "store": store,
                "name": product_name,
                "price per liter": price_per_liter,
                "product price": product_price,
                "product link": product_link,
            }
        )
    else:
        if price_per_liter is None:
            print("Product has no price per liter : ", product_link)
        else:
            print("Product has no price : ", product_link)


def calculate_liters(label: str, reverse_pattern: bool = False) -> float:
    """
    Calculate the amount of liters from the product name
    """
    if reverse_pattern:
        pattern = re.search(r"([0-9]+) X ([0-9]*\.[0-9]+)L?", label)
    else:
        pattern = re.search(r"([0-9]*\.[0-9]+)[l, L] [x, X] ([0-9]+)", label)
    liters_per_unit = float(pattern.group(1))
    amount = float(pattern.group(2))
    total_liters = liters_per_unit * amount
    return total_liters


def price_locator(label: str, int_price: bool = False) -> str:
    """
    Function loncate price in string and return price as float number
    """
    if int_price:
        pattern = re.search(r"\S*\d[\d,\.]*?\b", label).group()
    else:
        pattern = re.search(r"\d{1,4}(?:[.,]\d{3})*(?:[.,]\d{1,3})", label).group()
    return pattern


def convert_str_price_to_float(price: str) -> float:
    """
    Conver a string formated price into float
    """
    if "," in price:
        price = price.replace(",", ".")
    if price.count(".") > 1:
        price = price.replace(".", "", 1)
    return float(price)

def product_volume_locator(label: str) -> float:
    """
    Locate the volume of the product in Liters in the label
    """
    label = label.replace(" ","")
    pattern = re.search(r"([0-9]*\.[0-9]+)L|([0-9]+)L", label).group()
    return float(pattern[:-1])
