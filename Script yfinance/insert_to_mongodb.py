# pip install pymongo

import json
from pymongo import MongoClient

# Baca file JSON
json_file_path = "tickers_data.json"
with open(json_file_path, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Ubah jika connection string berbeda
db = client["bigdata_yfinance"]
collection = db["tickers_yfinance"]

# Masukkan data ke MongoDB
if data:
    collection.insert_many(data)
    print("Semua data berhasil dimasukkan ke MongoDB.")
else:
    print("Tidak ada data yang bisa dimasukkan ke MongoDB.")

print("Proses selesai.")
