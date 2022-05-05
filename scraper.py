
import requests

class Scraper:

    def __init__(self, response=None):
        self.response = self.get_status()

    def get_status(self, url):
        try:
            r = requests.get(url)
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




url = "https://pokeapi.co/api/v2/pokemon/ditto"
scrap = Scraper().get_status(url)
print(scrap)