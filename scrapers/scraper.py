"""
An abstract class to implement a web scraper that returns the information
(store name, product name, product price, price per liter of the product and 
the product link) from an online store 
"""
from abc import ABC, abstractmethod
from typing import Union
from bs4 import BeautifulSoup, ResultSet, Tag


class Scraper(ABC):

    link: str
    store: str
    all_products: dict

    @abstractmethod
    def get_page_soup(self, page_link: str) -> BeautifulSoup:
        """
        Receive as parameter the products page link and use "request" or "selenium web driver" 
        to get the HTML of the page and later create a BeautifulSoup object and return it as a result
        """
        pass

    @abstractmethod
    def get_product_info(self, soup: BeautifulSoup) -> ResultSet:
        """
        Receive as parameter a BeautifulSoup object , finds HTML tag that contain all the product 
        information an return a ResultSet object with all products information
        """
        pass

    @abstractmethod
    def get_product_name(self, product: Tag) -> str:
        """
        Receive as parameter a Tag object and returns the name of the product as string
        """
        pass

    @abstractmethod
    def get_product_price(self, product: Tag) -> Union[float, None]:
        """
        Receive as parameter a Tag object and returns the product price as float 
        or None if the price was not found
        """
        pass

    @abstractmethod
    def get_price_per_liter(self, product: Tag) -> Union[float, None]:
        """
        Receive as parameter a Tag object and returns the product price per liter as float 
        or None if the price was not found
        """
        pass

    @abstractmethod
    def get_product_link(self, product: Tag) -> str:
        """
        Receive as parameter a Tag object and returns the product link as string
        """
        pass

    @abstractmethod
    def store_product(
        self,
        product_name: str,
        price_per_liter: Union[float, None],
        product_price: Union[float, None],
        product_link: str,
    ) -> None:
        """
        Receive as parameter the "product name", "price per liter", "product price" 
        and "product link" and saves all extracted information in a dictionary
        """
        pass

    @abstractmethod
    def run_scraper(self) -> dict:
        """
        Performs the logical sequence to open the page, extract the information 
        of all products and return a dictionary with the information of all the products on the page
        """
        pass
