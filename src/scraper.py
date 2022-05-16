import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
import os
from os.path import join
import tkinter as tk
from tkinter import simpledialog
import uuid as uid


class Data:
    # constructor with datafields.
    def __init__(self, uuid, product_id=None, product_name=None, price=None, summary=None):
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


class Scraper:
    default_url = "https://www.arcadeworlduk.com/"

    def __init__(self, response=None, get_url=default_url, **kwargs):
        self.response = self.get_status if response is None else response
        self.get_url = get_url
        self.search_query = self.gui_search("Enter product name: ")

    @staticmethod
    def gui_search(query: str):
        root = tk.Tk()
        root.withdraw()

        while True:
            try:
                # the input dialog
                user_inp = simpledialog.askstring(title="Enter Product name",
                                                  prompt=query)
                return user_inp

            except ValueError as e:
                raise

    def get_status(self, page_number=None):
        try:
            r = requests.get(self.search_product()) if page_number is None else requests.get(
                self.pagination(page_number))
            return r
        except requests.exceptions.Timeout:
            print("Session Timeout")
            # Maybe set up for a retry, or continue in a retry loop
        except requests.exceptions.TooManyRedirects:
            print("Url is bad try a different one")
            # Tell the user their URL was bad and try a different one
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            raise SystemExit(e)

    @staticmethod
    def store_data(data: dict):
        # method stores raw data into a local directory
        path = "/home/hamza/PycharmProjects/AICoreProject_DataCollection/raw_data"
        is_exist = os.path.exists(path)

        if not is_exist:
            os.makedirs(path)
            print("New directory created!")
        if not isinstance(data, dict):
            raise TypeError
        else:
            with open(join(path, "data.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                print("json file created!")

    def search_product(self):
        return f"{self.get_url}search.php?search_query={self.search_query}&section=product"

    def return_soup(self, page_number=None):
        # return soup object
        request = self.get_status() if page_number is None else self.get_status(page_number)
        soup = BeautifulSoup(request.text, "html.parser")
        return soup

    def print_html(self):
        # prints the html in a more readable format
        soup = self.return_soup()
        return soup.prettify()

    def pagination(self, page_num: int):
        # Allows user to extract data through each page, by manipulating e url directly
        return f"{self.get_url}search.php?page={page_num}&section=product&search_query={self.search_query}"

    def extract_css_selector(self, soup_obj=None, text: str = None, attribute=None):
        empty_list = []

        soup_obj = self.return_soup() if soup_obj is None else soup_obj

        css_selector = soup_obj.select(text)

        for container in css_selector:
            empty_list.append(container[attribute])
        return empty_list

    def extract_into_list(self, tag: str = None, class_str=None, href=False, index=None, soup=None, attrs=None,
                          css_selector=None):
        # Custom function built to extract data from website. Arguments correlate to the Beautifulsoup "find_all"
        # method. User can customize what they want to extract
        empty_list = []

        soup = self.return_soup() if soup is None else soup

        all_tags = soup.find_all(tag, class_=class_str, href=href, attrs=attrs)

        if not isinstance(soup, BeautifulSoup):
            # checks if object is of bs4 type, in case an argument was passed for the "soup" parameter
            raise TypeError
        else:
            if index is None:
                for container in all_tags:
                    name = container.text
                    if tag is "img":
                        if "http" in container.get('src'):
                            path = "/home/hamza/PycharmProjects/AICoreProject_DataCollection/images"
                            img = container.get('src')
                            print(img)
                            with open(join(path, img), "wb") as f:
                                f.write(requests.get(img).content)
                                print(f)
                        else:
                            img = container['src']
                            print(img)
                    else:
                        if re.search(r"\w+[\s]|[£]\d+", name):
                            empty_list.append(name)

            else:
                for container in all_tags[index]:
                    name = container.text
                    if re.search(r"\w+[\s]|[£]\d+", name):
                        empty_list.append(name)

        return empty_list

    @staticmethod
    def generate_id(results: list = None):
        # generate unique global id with UUID package.
        unique_id = []

        for id in enumerate(results):
            uuidv4 = uid.uuid4()
            unique_id.append(str(uuidv4))

        return unique_id


def main(iterate=False):
    page_counter = 1
    scraper = Scraper()
    if iterate is True:
        while True:
            try:
                page_counter += 1
                data = scraper.return_soup(page_counter)
                product_name = scraper.extract_into_list(tag="a", href=True, soup=data, attrs={"data-event-type": True})
                price = scraper.extract_into_list(tag="span", class_str="price", soup=data,
                                                  attrs={"data-product-price-with"
                                                         "-tax": True})
                summary = scraper.extract_into_list(tag="p", class_str="card-summary", soup=data)
                data_fields = Data(product_name, price, summary)
                df = pd.DataFrame(data_fields.to_dict())
                print(data_fields)
            except Exception as ex:
                print(ex)
                print("probably last page:", page_counter)
                break
    else:
        try:
            product_name = scraper.extract_into_list(tag="a", href=True, attrs={"data-event-type": True})
            product_id = scraper.extract_css_selector(text="li.product > article", attribute='data-entity-id')
            unique_id = scraper.generate_id(product_name)
            price = scraper.extract_into_list(tag="span", class_str="price", attrs={"data-product-price-with"
                                                                                    "-tax": True})
            summary = scraper.extract_into_list(tag="p", class_str="card-summary")
            # img = scraper.extract_into_list(tag="img", soup=data)
            data_fields = Data(unique_id, product_id, product_name, price, summary)
            scraper.store_data(data_fields.to_dict())
        except Exception as ex:
            print(ex)
            raise


if __name__ == "__main__":
    main()
    # scraper = Scraper()
    # id = scraper.extract_css_selector(text="li.product > article", attribute='data-entity-id')
    # print(id)

    li.product: nth - child(2) > article:nth - child(1) > figure: nth - child(1) > a:nth - child(1) > div: nth - child(
        1) > img:nth - child(1)