import requests
import time

from transformers import pipeline

# Load a zero-shot classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

stores = [
    "freshco",
    "zehrs"
]

all_matched_items = []

from enum import Enum

# Labels for zero-shot classification
class FoodLabel(Enum):
    DAIRY = "Dairy Products"
    PROTEIN = "Protein Foods (Meat, Fish, Eggs, Beans, Nuts)"
    VEGETABLES = "Vegetables and fruits"
    GRAINS = "Grains(Breads, Cereals, Rice, Pasta)"
    FATS = "Fats, Oils"
    SWEETS = "Sweets"

candidate_labels = [label.value for label in FoodLabel]

def find_flyer_items(store : str, type : FoodLabel, confidence_threshold=0.6):
    """
    Fetch flyer items from the given store and return dairy products on sale using a zero-shot classification algorithm.

    Args:
        store (str): The name of the store used to build the flyer URL.
        type (FoodLabel): The type of items you want to identify in the flyer list.
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

        result = classifier(desc, candidate_labels)
        for lbl, score in zip(result["labels"], result["scores"]):
            if lbl == f"{type.value}" and score >= confidence_threshold:
                matched_items.append((desc, price, store, round(score, 2)))

    print(f"There are {len(matched_items)} {type.value} items in this weeks {store} flyer.")
    end = time.time()     # record end
    print(f"Took {end - start:.2f} to classify {len(all_items)} total items in this weeks {store} flyer.")

    return matched_items

searchType = FoodLabel.VEGETABLES

for store in stores:
    results = find_flyer_items(store, searchType)   # each call returns a list
    all_matched_items.extend(results) # combine into one big list

print(f"Total {searchType.value} items: {len(all_matched_items)}")

for desc, price, store, score in all_matched_items:
        print(f" - {desc} on sale @ {store} for {price} (confidence {score})")