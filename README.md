# Data Collection Pipeline

This project will involve the implementation of an industry grade data collection pipeline that runs scalably in the cloud.

## Table of Contents:
* [Technologies](#technologies)
* [Milestone 1](#milestone-1)
* [Milestone 2](#milestone-2)

## Technologies
* Pycharm 
* BeautifulSoup/request library

## Milestone 1
This mainly involved deciding which website to scrape. I decided that i will be scraping the website Arcade-World. The user will enter the product name which will then 
generate the results into a pandas dataframe object which can then be stored into a csv file.

## Milestone 2
This section will involve creating the scraper class. The class will include a number of methods to allow the user to extract the dataset they need through manipulating
the html code. These are the methods that will be included within the class initially:
```python
def gui_search(query: str):
# Using tkinter will allow user to enter product on a gui object rather then the terminal
def get_status(self):
# using request library this method will get the status_code for the url
def search_product(self):
# User can enter their product which will then be processed onto the website
def return_soup(self):
# Method to return BeautifulSoup object
def print_html(self):
# Uses Bs4.prettify to print html in readable format
def pagination(self):
# Method for allowing us to later loop through each page to extract the data
def extract_into_list(self):
# Method extracts results into a list

```
The data will then be stored into a second class labelled "Data" this will be then converted into a dictionary for later use
```python

class Data:
    # constructor with datafields.
    def __init__(self, uuid, product_id, product_name=None, price=None, summary=None):
        self.product_name = product_name
        self.price = price
        self.summary = summary
        self.uuid = uuid
        self.product_id = product_id

    def __repr__(self):
        return f"Unique ID={self.uuid}, Product ID={self.product_id} Product={self.product_name}, " \
               f"Price={self.price}, Summary={self.summary}"

    def to_dict(self):
        return {"Unique iD": self.uuid, "Product ID": self.product_id, "Product": self.product_name,
                "Price": self.price, "Summary": self.summary}
```

---
