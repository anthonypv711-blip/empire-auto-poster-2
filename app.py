from flask import Flask, render_template, request, redirect
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

BASE_URL = "https://www.empirefordinc.com/new-vehicles/"
PAGE_ID = "YOUR_PAGE_ID"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

posted = set()
skipped = set()

import requests

def get_inventory():
    url = "https://hippo.prod.core.autofi.io/api/v2/vehicles"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "autofiservice": "autofi-panda-prod:vehiclesV2",
        "dealers": "CLVT",
        "origin": "https://www.empirefordinc.com",
        "referer": "https://www.empirefordinc.com/",
        "user-agent": "Mozilla/5.0"
    }

    payload = {
        "filters": {
            "dealer": ["CLVT"]
        },
        "format": "json",
        "fields": [
            "year", "make", "model", "trim",
            "vin", "dealerRetailPrice", "msrp",
            "photoUrls"
        ],
        "limit": 50,
        "offset": 0
    }

    res = requests.post(url, json=payload, headers=headers)

    print("Status:", res.status_code)

    data = res.json()

    cars = []

    # IMPORTANT: structure is usually data["vehicles"] or data["results"]
    vehicles = data.get("vehicles") or data.get("results") or []

    for v in vehicles:
        title = f"{v.get('year')} {v.get('make')} {v.get('model')} {v.get('trim', '')}"

        price = v.get("dealerRetailPrice") or v.get("msrp") or "Call for price"

        image = None
        photos = v.get("photoUrls")
        if photos and len(photos) > 0:
            image = photos[0]

        cars.append({
            "title": title.strip(),
            "price": price,
            "image": image,
            "link": f"https://www.empirefordinc.com/searchnew.aspx?vin={v.get('vin')}"
        })

    return cars[:15]
def post_to_facebook(title, link):
    url = f"https://graph.facebook.com/{PAGE_ID}/feed"

    message = f"""
🔥 JUST ARRIVED 🔥

🚗 {title}

📍 Fall River, MA
👉 {link}

📲 Message me before it’s gone!
    """

    payload = {
        "message": message,
        "access_token": ACCESS_TOKEN
    }

    requests.post(url, data=payload)

@app.route("/")
def index():
    cars = get_inventory()

    filtered = [
        car for car in cars
        if car["link"] not in posted and car["link"] not in skipped
    ]

    return render_template("index.html", cars=filtered)

@app.route("/post", methods=["POST"])
def post():
    link = request.form["link"]
    title = request.form["title"]

    post_to_facebook(title, link)
    posted.add(link)

    return redirect("/")

@app.route("/skip", methods=["POST"])
def skip():
    link = request.form["link"]
    skipped.add(link)
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
