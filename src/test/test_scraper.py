import os
import unittest
import sys
from bs4 import BeautifulSoup
from mock import patch

path_parent = os.path.dirname(os.getcwd())
path = os.path.join(path_parent, "main")
sys.path.insert(0, path)

import scraper as sc


class TestCase(unittest.TestCase):
    scrape_test = sc.Scraper(get_url="https://www.arcadeworlduk.com/")

    def test_returns_true_if_url_exists(self):
        with patch('requests.get') as mock_request:
            # get status_code with the intended code of 200

            mock_request.return_value.status_code = 200

            self.assertTrue(self.scrape_test.get_status.status_code)

    def test_returns_False_if_url_exists(self):
        with patch('requests.get') as mock_request:
            # get status_code with the intended result 404
            scrape_test_fail = sc.Scraper(get_url="https://www.arcadeworlduk.com/nonresultintended")

            mock_request.return_value.status_code = 404

            self.assertFalse(scrape_test_fail.get_status.status_code)

    def test_instance(self):
        # tests whether object returned is of BeautifulSoup type
        self.assertIsInstance(self.scrape_test.return_soup(), BeautifulSoup)


if __name__ == '__main__':
    unittest.main()

