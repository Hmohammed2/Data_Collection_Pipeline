import logging

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from os.path import join
import tkinter as tk
from tkinter import simpledialog
import uuid as uid
import boto3
from botocore.exceptions import ClientError


class Data:
    # constructor with datafields.
    def __init__(self, uuid=None, product_id=None, product_name=None, price=None, summary=None, images=None):
        self.product_name = product_name
        self.price = price
        self.summary = summary
        self.uuid = uuid
        self.product_id = product_id
        self.images = images

    def __repr__(self):
        return f"Unique ID={self.uuid}, Product ID={self.product_id} Product={self.product_name}, " \
               f"Price={self.price}, Summary={self.summary}, Images={self.images}"

    def to_dict(self):
        # Method converts list into dictionary which will be later used to store in json file
        return {"Unique iD": self.uuid, "Product ID": self.product_id, "Product": self.product_name,
                "Price": self.price, "Summary": self.summary, "Images": self.images}


class Scraper:
    default_url = "https://www.arcadeworlduk.com/"

    def __init__(self, response=None, get_url=default_url, search_item=None):
        self.response = self.get_status if response is None else response
        self.get_url = get_url
        self.search_query = self.gui_search if search_item is None else search_item

    @staticmethod
    def gui_search(query: str):
        root = tk.Tk()
        root.withdraw()

        user_inp = simpledialog.askstring(title="Enter Product name",
                                          prompt="Enter product name: ")
        return user_inp

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

    def store_data(self, data: dict):
        """
        Method stores raw data into a local directory. Working directory is found dynamically and stores it in a
        json file
        """

        # Dynamically create the raw data folder
        path = f"{self.get_parent_dir(os.getcwd(), 1)}/raw_data"

        # File path is validated first to see if it exists
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

    @staticmethod
    def upload_file(filename, bucket, object_name=None):
        """ Uploads a file onto a s3 bucket
        : param: filename = the file that is to be uploaded
        : param: nucket = the s3 bucket that it will be uploaded to
        : param: object_name = s3 object name, if unspecified default to filename
        """
        if object_name is None:
            object_name = os.path.basename(filename)

        # Upload the file
        s3_client = boto3.client("s3")
        try:
            response = s3_client.upload_file(filename, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def search_product(self):
        # Using the url i can use this to manipulate the search criteria to my liking.
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

    @staticmethod
    def get_parent_dir(path, levels=1):
        # function allows me to customise the amount of levels i want the parent directory to go back to.
        common = path
        for i in range(levels+1):
            common = os.path.dirname(common)

        return common

    def extract_css_selector(self, soup_obj=None, text: str = None, attribute=None, counter=None):
        # initialise empty list
        empty_list = []

        soup_obj = self.return_soup() if soup_obj is None else soup_obj

        css_selector = soup_obj.select(text)

        if counter is not None:
            page_count = counter
        else:
            page_count = 0

        for container in css_selector:
            # checks if html string contains http to verify if attribute is either a href or an img attribute
            if "http" in container[attribute]:
                page_count += 1
                path = os.path.join(self.get_parent_dir(os.getcwd(), 1), "images")
                img = container[attribute]
                with open(join(path, f"image{page_count}.jpeg"), "wb") as f:
                    f.write(requests.get(img).content)
                    empty_list.append(container[attribute])
            else:
                empty_list.append(container[attribute])
        return empty_list

    def extract_into_list(self, tag: str = None, class_str=None, href=False, index=None, soup=None, attrs=None):
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

        # loop through each record, creating a unique id
        for id in enumerate(results):
            uuidv4 = uid.uuid4()
            unique_id.append(str(uuidv4))

        return unique_id


def main(iterate=False):
    page_counter = 1
    scraper = Scraper(search_item="Sanwa")
    if iterate is True:
        data_dict = {"Unique iD": [], "Product ID": [], "Product": [], "Price": [], "Summary": [], "Images": []}
        while True:
            try:
                count = sum([len(listelement) for listelement in data_dict["Unique iD"]])
                page_counter += 1
                data = scraper.return_soup(page_counter)
                product_name = scraper.extract_into_list(tag="a", href=True, attrs={"data-event-type": True}, soup=data)
                product_id = scraper.extract_css_selector(text="li.product > article", attribute='data-entity-id')
                unique_id = scraper.generate_id(product_name)
                price = scraper.extract_into_list(tag="span", class_str="price", attrs={"data-product-price-with"
                                                                                        "-tax": True}, soup=data)
                summary = scraper.extract_into_list(tag="p", class_str="card-summary", soup=data)
                img = scraper.extract_css_selector(text="li.product > article > figure > a > div > img",
                                                   attribute="data-src", counter=count)
                data_fields = Data(unique_id, product_id, product_name, price, summary, img)

                if bool(data_fields.to_dict()):
                    results = data_fields.to_dict()
                    for key, value in results.items():
                        data_dict[key].append(value)
                else:
                    print("No Results!")
                    break

                print(page_counter)
                print(data_dict)

                if page_counter == 5:

                    # Store as a json file
                    scraper.store_data(data_dict)

                    # upload file onto s3 scalably
                    path = f"{scraper.get_parent_dir(os.getcwd(), 1)}/raw_data"
                    scraper.upload_file(f"{path}/data.json", "my-scrape-bucket")
                    break

            except Exception as ex:
                print(ex)
                print("probably last page:", page_counter)
                raise
    else:
        try:
            product_name = scraper.extract_into_list(tag="a", href=True, attrs={"data-event-type": True})
            product_id = scraper.extract_css_selector(text="li.product > article", attribute='data-entity-id')
            unique_id = scraper.generate_id(product_name)
            price = scraper.extract_into_list(tag="span", class_str="price", attrs={"data-product-price-with"
                                                                                    "-tax": True})
            summary = scraper.extract_into_list(tag="p", class_str="card-summary")
            img = scraper.extract_css_selector(text="li.product > article > figure > a > div > img", attribute="data-src")
            data_fields = Data(unique_id, product_id, product_name, price, summary, img)
            if bool(data_fields.to_dict()):
                scraper.store_data(data_fields.to_dict())
                path = f"{scraper.get_parent_dir(os.getcwd(), 1)}/raw_data"
                scraper.upload_file(f"{path}/data.json", "my-scrape-bucket")
            else:
                print("No Results!")
        except Exception as ex:
            print(ex)
            raise


if __name__ == "__main__":
    # main(True)