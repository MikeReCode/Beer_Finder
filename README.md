# Beer_Finder
This is an application that collects information on beer prices in various romanian stores and creates a JSON file with the information of all the beers. See `beer.json` file to check the output (products sorted by "price per liter").

### Necessary libraries:

- selenium
- webdriver-manager
- beautifulsoup4
- lxml

### How it works:

The application uses multiprocessing to run 6 scrapes at the same time which will collect information about beer prices in 6 different romanian stores and will gather all the information collected in a JSON file.

All scrapes inherit from the same abstract class called "Scraper" and they all return a dictionary object with the information collected from a specific store.

### How to use it:

Install requirements from `requirements.txt` and run `beer_api.py`, when the process is finished `beers.json` will be updated.

Enjoy your beer! :beer: :smile:
