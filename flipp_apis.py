import requests
import time

class Flipp():
    BASE_URL = "https://api.flipp.com/v2"
    
    def __init__(self, postal_code: str = "N2K1Y7", sid: str = "8552038072202149"):
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; FlyerBot/1.0)"
        }
        self.postal_code = postal_code
        self.sid = sid

    def search_by_item(self, search_item: str):
        url = f"https://cdn-gateflipp.flippback.com/bf/flipp/items/search?locale=en-ca&postal_code={self.postal_code}&sid=&q={search_item}"
        
        resp = requests.get(url, headers=self.headers)
        data = resp.json()

        all_items = data.get("items", [])
        all_ecom_items = data.get("ecom_items", [])

        return all_items #+ all_ecom_items

    def find_flyers_by_store(self, merchant: str):
        flyer_url = f"https://dam.flippenterprise.net/api/flipp/data?locale=en&postal_code={self.postal_code}&sid={self.sid}"
        
        resp = requests.get(flyer_url, headers=self.headers)
        data = resp.json()

        all_flyers = data.get("flyers", [])
        matched_flyers = [flyer for flyer in all_flyers if flyer.get("merchant") != None and flyer.get("merchant").lower()== merchant.lower()]

        return matched_flyers
    
    def _find_all_items_by_flyer(self, flyer_id: str):
        flyer_url = f"https://dam.flippenterprise.net/api/flipp/flyers/{flyer_id}/flyer_items?locale=en"

        resp = requests.get(flyer_url, headers=self.headers)

        return resp.json()
    
    def find_all_items_by_store(self, merchant: str):
        matched_flyers = self.find_flyers_by_store(merchant)

        all_items = []
        for flyer in matched_flyers:
            flyer_id = flyer.get("id")
            data = self._find_all_items_by_flyer(flyer_id)
            all_items += data

        print(f"Found {len(all_items)} total items in this {len(matched_flyers)} '{merchant}' flyer(s).")
        return all_items
    
    def matched_items_as_tuple(self, matched_items_list: list):
        """
        Fetch flyer items from the given merchant and return items matching your criteria using string matching.

        Args:
            merchant (str): The name of the merchant used to build the flyer URL.
            search_item (str): The item you want to find in a flyer.

        Returns:
            list of tuples: [(description, price, confidence), ...]
        """
        start = time.time()   # record start
        
        matched_items = []
        #For all items that match the search string, get the details (sale, current price, etc)
        for item in matched_items_list:
            item_details = self._get_item_details(item.get("id"))
            sale_details = f"Item: [Found {item_details.get("name")}] @ [{item_details.get("current_price")}] {item_details.get("sale_story")}"
            if(item_details.get("original_price") != None):
                sale_details += f", originally [{item_details.get("original_price")}]"
            sale_details += f" at [{item_details.get("merchant")}]."
            print(sale_details)
            matched_items.append((item_details.get("name"), 0.0 if item_details.get("current_price") == None or item_details.get("current_price") =="" else float(item_details.get("current_price")), item_details.get("merchant")))
        #fuzzy_items = [word for word in all_items if SequenceMatcher(None, search_item, word.get("name")).ratio() > .8] 

        #print(f"There are {len(matched_items)} {search_item} items in this weeks {store} flyer.")
        #print(f"There are {len(fuzzy_items)} {fuzzy_items} items in this weeks {store} flyer.")
        
        end = time.time()     # record end
        sorted_by_price = sorted(matched_items, key=lambda x : x[1])

        return sorted_by_price
    
    def _get_item_details(self, item_id: str):
        """
        Retrieves the details of a flyer item from the Flipp API.
        Args:
            item_id (str): The unique identifier of the flyer item.
        Returns:
            dict: A dictionary containing the details of the flyer item as returned by the API.
        Raises:
            requests.exceptions.RequestException: If the HTTP request fails.
            ValueError: If the response cannot be decoded as JSON.
        """
        item_url = f"https://dam.flippenterprise.net/api/flipp/flyer_items/{item_id}?locale=en&sid=8552038072202149&postal_code=N2K1Y7"

        resp = requests.get(item_url, headers=self.headers)
        data = resp.json()

        return data