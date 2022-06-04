import os
import unittest
import sys
from bs4 import BeautifulSoup
import mock

path_parent = os.path.dirname(os.getcwd())
path = os.path.join(path_parent, "main")
sys.path.insert(0, path)

import scraper as sc


class TestCase(unittest.TestCase):
    scrape_test = sc.Scraper(search_item="Sanwa")

    def setup(self):
        # create a mock which will replace the request library
        self.mock_object = mock.Mock()
        #
        self.old_object = self.scrape_test
        #

    @mock.patch('scraper.os')
    @mock.patch('scrap.os.path')
    def store_data_test(self, mock_os, mock_path):

        reference = self.scrape_test
        mock_path.isfile.return_value = False

        reference.store_data()
        self.assertFalse(mock_os.remove_called, "Failed to remove file if not present!")

        mock_path.isfile.return_value = True

        reference.store_data()
        mock_os.remove.assert_called_with()

    def test_instance(self):
        # tests whether object returned is of BeautifulSoup type
        self.assertIsInstance(self.scrape_test.return_soup(), BeautifulSoup)

    def test_result(self):
        # Tests whether function returned is of list type, and whether there is any results
        product_name = self.scrape_test.extract_into_list(tag="a", href=True, attrs={"data-event-type": True})
        product_id = self.scrape_test.extract_css_selector(text="li.product > article", attribute='data-entity-id')

        self.assertIsInstance(product_name, list)
        self.assertIsInstance(product_id, list)


if __name__ == '__main__':
    unittest.main()

