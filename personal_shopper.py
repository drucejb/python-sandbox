import requests
import time

from transformers import pipeline

# Load a zero-shot classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

stores = [
    "freshco",
    "rexall"
]

all_matched_items = []

from enum import Enum

# Labels for zero-shot classification


def find_flyer_items(store : str, search_item : str, confidence_threshold=0.6):
    """
    Fetch flyer items from the given store and return items matching your criteria using a zero-shot classification algorithm.

    Args:
        store (str): The name of the store used to build the flyer URL.
        search_item (str): The item you want to find in a flyer.
        confidence_threshold (float): Minimum confidence to consider an item meets the 'type' classification.

    Returns:
        list of tuples: [(description, price, confidence), ...]
    """
    start = time.time()   # record start
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; FlyerBot/1.0)"
    }

    url = f"https://cdn-gateflipp.flippback.com/bf/flipp/items/search?locale=en-ca&postal_code=N2M1W5&sid=&q={store}"

    resp = requests.get(url, headers=headers)
    data = resp.json()

    matched_items = []
    all_items = data.get("items", [])

    for hit in all_items:
        desc = hit.get("name")
        price = hit.get("current_price")
        if not desc:
            continue

        result = classifier(desc, candidate_labels=[search_item, "not " + search_item])
        for lbl, score in zip(result["labels"], result["scores"]):
            if lbl == f"{search_item}" and score >= confidence_threshold:
                matched_items.append((desc, price, store, round(score, 2)))

    print(f"There are {len(matched_items)} {search_item} items in this weeks {store} flyer.")
    end = time.time()     # record end
    print(f"Took {end - start:.2f} to classify {len(all_items)} total items in this weeks {store} flyer.")

    return matched_items

search_item = "toothpaste"

for store in stores:
    results = find_flyer_items(store, search_item)   # each call returns a list
    all_matched_items.extend(results) # combine into one big list

print(f"Total {search_item} items: {len(all_matched_items)}")

for desc, price, store, score in all_matched_items:
        print(f" - {desc} on sale @ {store} for {price} (confidence {score})")