import json
from pymongo import MongoClient

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]
collection = db["articles2"]

# Buka file scraped_market_data.json
with open("scraped_market_data.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Memasukkan data ke MongoDB
for article in articles:
    if not collection.find_one({"judul": article["judul"]}):
        collection.insert_one(article)
        print(f"Artikel '{article['judul']}' dimasukkan ke MongoDB.")
    else:
        print(f" Artikel '{article['judul']}' sudah ada di database.")

print("Semua data selesai dimasukkan ke MongoDB.")