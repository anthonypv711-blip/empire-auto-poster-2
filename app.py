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

def get_inventory():
    url = "https://www.empirefordinc.com/apis/inventory/vehicles?type=new"

    res = requests.get(url)
    data = res.json()

    cars = []

    for vehicle in data.get("vehicles", []):
        title = f"{vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}"
        link = "https://www.empirefordinc.com" + vehicle.get("vdp_url", "")

        cars.append({
            "title": title,
            "link": link
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
