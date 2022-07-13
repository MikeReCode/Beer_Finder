""" This program uses multiprocessing to use all Scrapers at the same time and generate a JSON file with the results """
import multiprocessing as mp
import time
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from scrapers.scraperaltex import AltexScraper
from scrapers.scraperpeny import PennyScraper
from scrapers.scraperemag import EmagScraper
from scrapers.scraperauchan import AuchanScraper
from scrapers.scraperfreshful import FreshfulScraper
from scrapers.scrapermegaimage import MegaImageScraper


def runaltex(queue):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('user-agent=Type user agent here')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=chrome_options)
    driver.implicitly_wait(10)
    s = AltexScraper(driver)
    r = s.run_scraper()
    queue.put(r)

def runpenny(queue):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('user-agent=Type user agent here')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=chrome_options)
    driver.implicitly_wait(10)
    s = PennyScraper(driver)
    r = s.run_scraper()
    queue.put(r)

def runmegaimage(queue):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Type user agent here')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=chrome_options)
    driver.implicitly_wait(10)
    s = MegaImageScraper(driver)
    r = s.run_scraper()
    queue.put(r)

def runemag(queue):
    s = EmagScraper()
    r = s.run_scraper()
    queue.put(r)

def runauchan(queue):
    s = AuchanScraper()
    r = s.run_scraper()
    queue.put(r)

def runfreshful(queue):
    s = FreshfulScraper()
    r = s.run_scraper()
    queue.put(r)




if __name__ == '__main__':
    # add to the process list all the scrapers you want to run 
    process = [runaltex, runpenny, runmegaimage, runemag, runauchan, runfreshful]
    vars = {}

    # Starts all processes from the "process" list and creates a Queue object for every process 
    # than stores the running process and its respective Queue in a dictionary as key value pair
    for target in process:
        queue = mp.Queue()
        proces = mp.Process(target=target, args=(queue,))
        proces.start()
        vars[target] = queue

    # wait until all processes are finished, checking every second if the queues are empty or not
    not_finish = True
    while not_finish:
        time.sleep(1)
        process_finish = []
        for i in vars.values():
            if i.empty():
                process_finish.append(False)
            else:
                process_finish.append(True)
        if False not in process_finish:
            not_finish = False

    # create a dictionary with all the results 
    all_products = dict()
    all_products["products"] = list()
    for queue in vars.values():
        store = queue.get()
        all_products["products"] = all_products["products"] + store["products"]

    # sorted by price per liter 
    s = sorted(all_products["products"], key=lambda x: x["price per liter"]) 

    json_object = json.dumps(s, indent = 4) 
    with open("beers.json", "w") as outfile:
        outfile.write(json_object)

    # total numer os products 
    print("Total number of scraped products: ", len(s))
