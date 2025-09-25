import requests
import time
import os

from transformers import pipeline
from flipp_apis import Flipp

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

all_matched_items = []

def send_slack_message(text: str):
    payload = {"text": text}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        raise ValueError(f"Request to Slack returned error {response.status_code}, response: {response.text}")


@staticmethod
def search_by_item(search_item: str, stores = []):
    start = time.time()   # record start
    flipp = Flipp()

    found_items = []
    if stores is None or len(stores) == 0:
        all_items = flipp.search_by_item(search_item)
        found_items = flipp.matched_items_as_tuple(all_items)
        end = time.time() 
    else:
        for merchant in stores:
            all_items = flipp.find_all_items_by_store(merchant)
            matched_items1 = [item for item in all_items if item.get("name") != None and search_item.lower() in item.get("name").lower()]
            all_matched_items.extend(flipp.matched_items_as_tuple(matched_items1)) # combine into one big list  
            found_items = all_matched_items
        end = time.time()     # record end  
    print(f"Took {end - start:.2f} to search for {search_item} in this weeks {stores} flyer(s).")
    if len(found_items) > 0:            
        send_slack_message(f"🔥 {search_item} found on sale today:\n" + "\n".join([
            f"${price:.2f} for [{desc}] at {merchant}" if price != 0.0
            else f"{sale_story} for [{desc}] at {merchant}"
            for desc, price, sale_story, merchant in found_items
            if not (price == 0.0 and sale_story == "")
        ]))
    return found_items
    

#main program logic
#found_items = search_by_item("CeraVe")
#search_by_item("summer fridays")
#search_by_item("mario badescu")
#search_by_item("byoma")
#search_by_item("the ordinary")
#search_by_item("toaster", ["Canadian Tire"])
search_by_item("bread")